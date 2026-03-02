import traceback

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.models.batch import Batch, ValidationStatus
from app.models.product import Product
from app.models.ai_score import AIScore
from app.services.change_analyzer import classify_change
from app.services.ai_engine import generate_ai_rating
from app.core.config import APP_BASE_URL
from app.crud.material import add_materials
from app.models.material import BatchMaterial

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
                .with_for_update()  # optional isolation lock
                .first()
            )

            if not product:
                raise ValueError("Product not found or not owned")

            # -------- 2. Extract Materials Safely --------
            materials_data = data.materials or []
            # Create batch without material field
            batch_payload = data.model_dump(exclude={"materials"}, exclude_none=True)
            batch = Batch(**batch_payload, product_id=product_id)
            db.add(batch)

            db.flush()  # ✅ ensures batch.id is generated

            # -------- 3. Add Materials --------
            add_materials(
                db=db,
                materials=materials_data,
                batch_id=batch.id,
            )

            # -------- 4. Intelligent Validation --------
            previous = (
                db.query(Batch)
                .filter(Batch.product_id == product_id)
                .order_by(Batch.created_at.desc())
                .offset(1)
                .first()
            )

            ai_rating = None

            if previous:
                change_type = "Major" # classify_change(previous.material_info, materials_data,)

                if change_type == "no_change":
                    batch.validation_status = ValidationStatus.auto_verified

                    ai_rating = (
                        db.query(AIScore.final_score)
                        .filter(AIScore.batch_id == previous.id)
                        .scalar()
                    )

                elif change_type == "minor":
                    batch.validation_status = ValidationStatus.ai_review
                    ai_rating = generate_ai_rating()

                else:
                    batch.validation_status = ValidationStatus.lab_required
                    ai_rating = generate_ai_rating()

            else:
                batch.validation_status = ValidationStatus.lab_required
                ai_rating = generate_ai_rating()

            # -------- 5. Store AI Score --------
            if ai_rating is not None:
                db.add(
                    AIScore(
                        batch_id=batch.id,
                        rating=ai_rating["rating"],
                        reasoning=ai_rating["reasoning"],
                    )
                )

        # 🔒 Commit happens automatically here

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