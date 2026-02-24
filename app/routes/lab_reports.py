from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case

from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole
from app.models.lab_report import LabReport
from app.models.batch import Batch
from app.models.product import Product

from app.schemas.lab_report import (
    LabReportCreate,
    LabReportUpdate,
    LabReportResponse,
)

from app.crud.lab_report import (
    create_lab_report,
    update_lab_report,
    delete_lab_report,
    get_lab_report_by_id,
    get_reports_by_lab_paginated,
    get_all_reports_paginated
)

router = APIRouter()

# ==========================================================
# 1️⃣ LAB DASHBOARD
# ==========================================================

@router.get("/my/stats")
def lab_dashboard(
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.lab))
):
    """Get dashboard stats for the lab user
    """
    stats = (
        db.query(
            func.count(LabReport.id).label("total"),
            func.sum(case((LabReport.verified == True, 1), else_=0)).label("verified"),
            func.sum(case((LabReport.verified == False, 1), else_=0)).label("pending"),
        )
        .filter(LabReport.lab_id == user.id)
        .first()
    )

    total_batches_tested = stats.total
    verified_reports = stats.verified
    pending_reports = stats.pending

    unique_products_tested = (
        db.query(func.count(distinct(Product.id)))
        .join(Batch, Batch.product_id == Product.id)
        .join(LabReport, LabReport.batch_id == Batch.id)
        .filter(LabReport.lab_id == user.id)
        .scalar()
    )

    recent_reports = (
        db.query(LabReport)
        .filter(LabReport.lab_id == user.id)
        .order_by(LabReport.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_batches_tested": total_batches_tested,
        "unique_products_tested": unique_products_tested,
        "verified_reports": verified_reports,
        "pending_reports": pending_reports,
        "recent_reports": recent_reports
    }


# ==========================================================
# 2️⃣ CREATE REPORT (LAB)
# ==========================================================

@router.post("/batch/{batch_id}", response_model=LabReportResponse)
def create_report(
    batch_id: int,
    data: LabReportCreate,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.lab))
):
    return create_lab_report(db, data, batch_id, user.id)


# ==========================================================
# 3️⃣ UPDATE REPORT (ADMIN ONLY)
# ==========================================================

@router.patch("/{report_id}", response_model=LabReportResponse)
def update_report(
    report_id: int,
    data: LabReportUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    report = update_lab_report(db, report_id, data)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# ==========================================================
# 4️⃣ DELETE REPORT (ADMIN ONLY)
# ==========================================================

@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    deleted = delete_lab_report(db, report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}


# ==========================================================
# 5️⃣ GET MY REPORTS (LAB - PAGINATED)
# ==========================================================

@router.get("/my")
def get_my_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    verified: bool | None = Query(None),
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.lab))
):
    skip = (page - 1) * limit

    items, total = get_reports_by_lab_paginated(
        db=db,
        lab_id=user.id,
        skip=skip,
        limit=limit,
        search=search,
        verified=verified
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


# ==========================================================
# 6️⃣ ADMIN - GET ALL REPORTS (PAGINATED)
# ==========================================================

@router.get("/")
def get_all_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    skip = (page - 1) * limit

    items, total = get_all_reports_paginated(
        db=db,
        skip=skip,
        limit=limit
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


# ==========================================================
# 7️⃣ GET SINGLE REPORT (PUBLIC)
# ==========================================================

@router.get("/{report_id}", response_model=LabReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = get_lab_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report