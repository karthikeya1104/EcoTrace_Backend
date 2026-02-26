from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.routes.auth import get_db
from app.models.batch import Batch, ValidationStatus
from app.models.user import UserRole
from app.models.product import Product
from app.core.roles import require_role

router = APIRouter()

@router.get("/pending-tests")
def pending_lab_tests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.lab))
):
    skip = (page - 1) * limit

    query = (
        db.query(Batch)
        .options(joinedload(Batch.product))
        .filter(
            Batch.validation_status == ValidationStatus.lab_required,
            ~Batch.lab_reports.any()  # ✅ No lab report exists
        )
    )

    if search:
        search_term = f"%{search}%"
        query = query.join(Batch.product).filter(
            or_(
                Batch.batch_code.ilike(search_term),
                Batch.manufacturing_location.ilike(search_term),
                Product.name.ilike(search_term),
            )
        )

    total = query.count()

    items = (
        query.order_by(Batch.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }