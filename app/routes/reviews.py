from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole
from app.schemas.review import ReviewCreate
from app.crud.review import create_or_update_review, get_consumer_dashboard, get_reviews_by_batch_paginated, get_reviews_by_product_paginated, get_review_summary, delete_review, get_user_reviews_paginated
from app.core.security import get_current_user_optional

router = APIRouter()

@router.post("/batch/{batch_id}")
def create_review(
    batch_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.consumer))
):
    return create_or_update_review(db, batch_id, user.id, data)


@router.get("/batch/{batch_id}")
def list_batch_reviews(
    batch_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    user_id = user.id if user else None  # ✅ FIX HERE

    items, total = get_reviews_by_batch_paginated(
        db,
        batch_id,
        user_id,
        skip,
        limit
    )

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/product/{product_id}")
def list_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    items, total = get_reviews_by_product_paginated(
        db, product_id, skip, limit
    )

    return {"items": items, "total": total}


@router.get("/batch/{batch_id}/summary")
def summary(
    batch_id: int,
    db: Session = Depends(get_db)
):
    return get_review_summary(db, batch_id)


@router.delete("/{review_id}")
def delete(
    review_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.consumer))
):
    return delete_review(db, review_id, user.id)


@router.get("/dashboard")
def consumer_dashboard(
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.consumer))
):
    return get_consumer_dashboard(db, user.id)


@router.get("/me")
def my_reviews(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.consumer))
):
    items, total = get_user_reviews_paginated(
        db, user.id, skip, limit
    )

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }