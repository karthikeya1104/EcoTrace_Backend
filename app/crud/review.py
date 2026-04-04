from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from app.models.review import Review
from app.models.batch import Batch, BatchStatus
from app.models.user import User

def create_or_update_review(db: Session, batch_id: int, user_id: int, data):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch.status != BatchStatus.verified:
        raise HTTPException(
            status_code=400,
            detail="Only verified batches can be reviewed"
        )

    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1–5")

    review = db.query(Review).filter(
        Review.batch_id == batch_id,
        Review.user_id == user_id
    ).first()

    if review:
        review.rating = data.rating
        review.comment = data.comment
    else:
        review = Review(
            batch_id=batch_id,
            user_id=user_id,
            rating=data.rating,
            comment=data.comment
        )
        db.add(review)

    db.commit()
    db.refresh(review)

    return review


def get_reviews_by_batch_paginated(
    db: Session,
    batch_id: int,
    user_id: int,
    skip: int,
    limit: int
):
    base_query = db.query(Review).filter(Review.batch_id == batch_id)

    total = base_query.count()

    rows = (
        db.query(
            Review.id,
            Review.rating,
            Review.comment,
            Review.created_at,
            Review.user_id,
            User.name.label("user_name")
        )
        .join(User, User.id == Review.user_id)
        .filter(Review.batch_id == batch_id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Transform → clean JSON
    items = [
        {
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at,
            "user": {
                "name": r.user_name
            },
            "is_mine": r.user_id == user_id
        }
        for r in rows
    ]

    return items, total


def get_reviews_by_product_paginated(
    db: Session,
    product_id: int,
    skip: int,
    limit: int
):
    query = (
        db.query(Review)
        .join(Batch, Batch.id == Review.batch_id)
        .options(joinedload(Review.user))
        .filter(Batch.product_id == product_id)
    )

    total = query.count()

    items = (
        query.order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


def get_review_summary(db: Session, batch_id: int):
    result = db.query(
        func.count(Review.id),
        func.avg(Review.rating)
    ).filter(Review.batch_id == batch_id).first()

    return {
        "total_reviews": result[0] or 0,
        "average_rating": round(result[1], 2) if result[1] else 0
    }

def delete_review(db: Session, review_id: int, user_id: int):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(review)
    db.commit()

    return {"message": "Deleted successfully"}


def get_consumer_dashboard(db: Session, user_id: int):
    # Rating distribution + total reviews
    stats = db.query(
        func.count(Review.id).label("total_reviews"),

        func.sum(case((Review.rating == 5, 1), else_=0)).label("five_star"),
        func.sum(case((Review.rating == 4, 1), else_=0)).label("four_star"),
        func.sum(case((Review.rating == 3, 1), else_=0)).label("three_star"),
        func.sum(case((Review.rating == 2, 1), else_=0)).label("two_star"),
        func.sum(case((Review.rating == 1, 1), else_=0)).label("one_star"),
    ).filter(Review.user_id == user_id).first()

    # Last 5 reviewed batches
    recent_reviews = (
        db.query(Review)
        .join(Batch, Batch.id == Review.batch_id)
        .options(joinedload(Review.batch))
        .filter(Review.user_id == user_id)
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_reviews": stats.total_reviews or 0,
        "ratings": {
            "5": stats.five_star or 0,
            "4": stats.four_star or 0,
            "3": stats.three_star or 0,
            "2": stats.two_star or 0,
            "1": stats.one_star or 0,
        },
        "recent_reviews": recent_reviews
    }


def get_user_reviews_paginated(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
):
    query = (
        db.query(Review)
        .join(Batch, Batch.id == Review.batch_id)
        .options(joinedload(Review.batch))
        .filter(Review.user_id == user_id)
    )

    total = query.count()

    items = (
        query.order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total