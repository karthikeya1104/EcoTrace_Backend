from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.batch import Batch, ValidationStatus
from app.models.product import Product
from app.models.ai_score import AIScore
from app.services.change_analyzer import classify_change
from app.services.ai_engine import generate_ai_score
from app.core.config import APP_BASE_URL


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
        _base_query(db)
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
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.manufacturer_id == manufacturer_id,
        )
        .first()
    )

    if not product:
        raise ValueError("Product not found or not owned")

    # prevent duplicate batch code per product
    exists = (
        db.query(Batch.id)
        .filter(
            Batch.product_id == product_id,
            Batch.batch_code == data.batch_code,
        )
        .first()
    )

    if exists:
        raise ValueError("Batch code already exists for this product")

    batch = Batch(**data.model_dump(), product_id=product_id)
    db.add(batch)
    db.flush()  # flush only, no commit yet

    # ---------- INTELLIGENT VALIDATION PIPELINE ----------

    previous = (
        db.query(Batch)
        .filter(Batch.product_id == product_id)
        .order_by(Batch.created_at.desc())
        .offset(1)
        .first()
    )

    ai_score_value = None

    if previous:
        change_type = classify_change(
            previous.material_info,
            data.material_info,
        )

        if change_type == "no_change":
            batch.validation_status = ValidationStatus.auto_verified

            prev_score = (
                db.query(AIScore.final_score)
                .filter(AIScore.batch_id == previous.id)
                .scalar()
            )
            ai_score_value = prev_score

        elif change_type == "minor":
            batch.validation_status = ValidationStatus.ai_review
            ai_score_value = generate_ai_score()["final_score"]

        else:
            batch.validation_status = ValidationStatus.lab_required
            ai_score_value = generate_ai_score()["final_score"]

    else:
        batch.validation_status = ValidationStatus.lab_required
        ai_score_value = generate_ai_score()["final_score"]

    if ai_score_value is not None:
        db.add(AIScore(batch_id=batch.id, final_score=ai_score_value))

    db.commit()

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