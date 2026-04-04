from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models.user import User
from app.models.product import Product
from app.models.batch import Batch, BatchStatus
from app.models.lab_report import LabReport


def get_admin_dashboard(db: Session):
    today = datetime.utcnow().date()

    # -------- USERS --------
    total_users = db.query(func.count(User.id)).scalar()

    users_by_role = (
        db.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )
    role_counts = {role.value: count for role, count in users_by_role}

    # -------- PRODUCTS --------
    total_products = db.query(func.count(Product.id)).scalar()

    # Top products by batches
    top_products = (
        db.query(
            Product.id,
            Product.name,
            func.count(Batch.id).label("batch_count")
        )
        .join(Batch, Batch.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.count(Batch.id).desc())
        .limit(5)
        .all()
    )

    # -------- BATCHES --------
    total_batches = db.query(func.count(Batch.id)).scalar()

    batch_status = (
        db.query(Batch.status, func.count(Batch.id))
        .group_by(Batch.status)
        .all()
    )
    batch_status_counts = {status.value: count for status, count in batch_status}

    batches_today = db.query(func.count(Batch.id)).filter(
        func.date(Batch.created_at) == today
    ).scalar()

    # -------- LAB REPORTS --------
    total_reports = db.query(func.count(LabReport.id)).scalar()

    verified_reports = db.query(func.count(LabReport.id)).filter(
        LabReport.verified == True
    ).scalar()

    reports_today = db.query(func.count(LabReport.id)).filter(
        func.date(LabReport.created_at) == today
    ).scalar()

    # -------- RESPONSE --------
    return {
        "users": {
            "total": total_users,
            "by_role": role_counts
        },
        "products": {
            "total": total_products,
            "top_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "batch_count": p.batch_count
                }
                for p in top_products
            ]
        },
        "batches": {
            "total": total_batches,
            "status": batch_status_counts,
            "today": batches_today
        },
        "lab_reports": {
            "total": total_reports,
            "verified": verified_reports,
            "pending": total_reports - verified_reports,
            "today": reports_today
        }
    }