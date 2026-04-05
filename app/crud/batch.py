import traceback

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.models.batch import Batch, BatchStatus, ValidationStatus
from app.models.product import Product
from app.models.ai_score import AIScore
from app.services.change_analyzer import classify_change
from app.services.ai_engine import generate_ai_rating
from app.core.config import APP_BASE_URL
from app.crud.material import add_materials
from app.models.material import BatchMaterial
from app.models.lab_report import LabReport

def extract_product_details(product):
    return {
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
    }


# ============================================================
# BASE QUERY (Reusable)
# ============================================================
def _base_query(db: Session):
    return db.query(Batch).options(joinedload(Batch.product))


# ============================================================
# LIST (Manufacturer Scoped + Pagination + Search)
# ============================================================
def list_batches(
    db,
    manufacturer_id: int,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    if page < 1:
        page = 1

    skip = (page - 1) * limit

    query = (
        db.query(Batch)
        .options(joinedload(Batch.product))
        .join(Batch.product)
        .filter(Product.manufacturer_id == manufacturer_id)
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Batch.batch_code.ilike(search_term),
                Product.name.ilike(search_term),
                Product.brand.ilike(search_term),
            )
        )

    total = query.count()

    items = (
        query.order_by(Batch.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, items


# ============================================================
# GET SINGLE (Manufacturer Scoped)
# ============================================================
def get_batch(db: Session, batch_id: int, manufacturer_id: int):
    return (
        db.query(Batch)
        .options(
            selectinload(Batch.product),
            selectinload(Batch.materials)
                .selectinload(BatchMaterial.material)  # 🔥 REQUIRED
        )
        .join(Batch.product)
        .filter(
            Batch.id == batch_id,
            Product.manufacturer_id == manufacturer_id,
        )
        .first()
    )


# ============================================================
# CREATE
# ============================================================
def create_batch(
    db: Session,
    product_id: int,
    manufacturer_id: int,
    data,
):
    try:
        with db.begin():  # 🔒 ACID transaction block

            # -------- 1. Validate Product Ownership --------
            product = (
                db.query(Product)
                .filter(
                    Product.id == product_id,
                    Product.manufacturer_id == manufacturer_id,
                )
                .with_for_update()
                .first()
            )

            if not product:
                raise ValueError("Product not found or not owned")

            # -------- 2. Extract Materials --------
            materials_data = data.materials or []

            batch_payload = data.model_dump(
                exclude={"materials"},
                exclude_none=True
            )

            batch = Batch(**batch_payload, product_id=product_id)
            db.add(batch)
            db.flush()

            # -------- 3. Add Materials --------
            add_materials(
                db=db,
                materials=materials_data,
                batch_id=batch.id,
            )

            # -------- 4. Fetch Previous Batch --------
            previous = (
                db.query(Batch)
                .filter(Batch.product_id == product_id)
                .order_by(Batch.created_at.desc())
                .offset(1)
                .first()
            )

            # -------- 5. Prepare Material Comparison --------
            previous_materials = []
            if previous:
                previous_materials = [
                    {
                        "name": bm.material.name,
                        "percentage": bm.percentage,
                    }
                    for bm in previous.materials
                ]

            current_materials = [
                m.model_dump()
                for m in materials_data
            ]

            ai_rating = None
            product_details = extract_product_details(product)

            # -------- 6. Validation Logic --------
            if previous:
                change_type = classify_change(
                    previous_materials,
                    current_materials
                )

                # ✅ NO CHANGE → reuse everything
                if change_type == "no_change":
                    batch.validation_status = ValidationStatus.auto_verified
                    batch.status = BatchStatus.verified

                    # ---- Reuse AI score ----
                    ai_rating = (
                        db.query(AIScore)
                        .filter(AIScore.batch_id == previous.id)
                        .order_by(AIScore.id.desc())
                        .first()
                    )

                    # ---- Reuse Lab Report ----
                    previous_lab = (
                        db.query(LabReport)
                        .filter(LabReport.batch_id == previous.id)
                        .order_by(LabReport.created_at.desc())
                        .first()
                    )

                    if previous_lab:
                        db.add(
                            LabReport(
                                batch_id=batch.id,
                                lab_id=previous_lab.lab_id,
                                analysis_data=previous_lab.analysis_data,
                                certifications=previous_lab.certifications,
                                safety_status=previous_lab.safety_status,
                                notes="Reused from previous batch",
                                lab_score=previous_lab.lab_score,
                                verified=True,
                            )
                        )

                # ✅ MINOR CHANGE → AI review
                elif change_type == "minor":
                    batch.validation_status = ValidationStatus.ai_review
                    ai_rating = generate_ai_rating(
                        product_details,
                        batch,
                        current_materials
                    )
                    batch.status = BatchStatus.verified

                # ✅ MAJOR CHANGE → Lab required
                else:
                    batch.validation_status = ValidationStatus.lab_required
                    ai_rating = generate_ai_rating(
                        product_details,
                        batch,
                        current_materials
                    )
                
            # ✅ FIRST BATCH
            else:
                batch.validation_status = ValidationStatus.lab_required
                ai_rating = generate_ai_rating(
                    product_details,
                    batch,
                    current_materials
                )

            # -------- 7. Store AI Score --------
            if ai_rating:
                if isinstance(ai_rating, dict):
                    db.add(
                        AIScore(
                            batch_id=batch.id,
                            rating=ai_rating["rating"],
                            reasoning=ai_rating["reasoning"],
                        )
                    )
                else:
                    # reused AI score object
                    db.add(
                        AIScore(
                            batch_id=batch.id,
                            rating=ai_rating.rating,
                            reasoning=ai_rating.reasoning,
                        )
                    )

        # 🔒 auto commit

    except IntegrityError:
        db.rollback()
        raise ValueError("Batch code already exists for this product")

    except Exception:
        db.rollback()
        print("Error creating batch:", traceback.format_exc())
        raise ValueError("Failed to create batch")

    return (
        _base_query(db)
        .filter(Batch.id == batch.id)
        .first(),
        f"{APP_BASE_URL}/public/batch/{batch.id}",
    )


# ============================================================
# UPDATE
# ============================================================
def update_batch(
    db: Session,
    batch_id: int,
    manufacturer_id: int,
    data,
):
    batch = (
        db.query(Batch)
        .join(Batch.product)
        .filter(
            Batch.id == batch_id,
            Product.manufacturer_id == manufacturer_id,
        )
        .first()
    )

    if not batch:
        raise ValueError("Batch not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(batch, key, value)

    db.commit()

    return (
        _base_query(db)
        .filter(Batch.id == batch.id)
        .first()
    )


# ============================================================
# DELETE
# ============================================================
def delete_batch(
    db: Session,
    batch_id: int,
    manufacturer_id: int,
):
    batch = (
        db.query(Batch)
        .join(Batch.product)
        .filter(
            Batch.id == batch_id,
            Product.manufacturer_id == manufacturer_id,
        )
        .first()
    )

    if not batch:
        raise ValueError("Batch not found")

    db.delete(batch)
    db.commit()