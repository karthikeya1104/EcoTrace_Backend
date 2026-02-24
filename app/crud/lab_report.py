from http.client import HTTPException

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, cast, String
from app.models.lab_report import LabReport
from app.models.batch import Batch


# ==========================================================
# CREATE
# ==========================================================

def create_lab_report(db: Session, data, batch_id: int, lab_id: int):
    # Ensure batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise ValueError("Batch not found")

    # Optional: prevent duplicate report for same batch by same lab
    existing = (
        db.query(LabReport)
        .filter(
            LabReport.batch_id == batch_id,
            LabReport.lab_id == lab_id
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "Report already exists for this batch")

    report = LabReport(
        batch_id=batch_id,
        lab_id=lab_id,
        test_summary=data.test_summary,
        certifications=data.certifications,
        eco_rating=data.eco_rating,
        lab_score=data.lab_score,
        verified=False
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


# ==========================================================
# GET SINGLE
# ==========================================================

def get_lab_report_by_id(db: Session, report_id: int):
    return (
        db.query(LabReport)
        .options(joinedload(LabReport.batch))
        .filter(LabReport.id == report_id)
        .first()
    )


# ==========================================================
# UPDATE
# ==========================================================

def update_lab_report(db: Session, report_id: int, data):
    report = get_lab_report_by_id(db, report_id)
    if not report:
        return None

    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(report, key, value)

    db.commit()
    db.refresh(report)
    return report


# ==========================================================
# DELETE
# ==========================================================

def delete_lab_report(db: Session, report_id: int):
    report = get_lab_report_by_id(db, report_id)
    if not report:
        return False

    db.delete(report)
    db.commit()
    return True


# ==========================================================
# PAGINATED HELPERS
# ==========================================================

def get_reports_by_lab_paginated(
    db: Session,
    lab_id: int,
    skip: int,
    limit: int,
    search: str | None = None,
    verified: bool | None = None
):
    query = (
        db.query(LabReport)
        .join(LabReport.batch)
        .options(joinedload(LabReport.batch))
        .filter(LabReport.lab_id == lab_id)
    )

    if verified is not None:
        query = query.filter(LabReport.verified == verified)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                LabReport.test_summary.ilike(search_term),
                LabReport.certifications.ilike(search_term),
                cast(LabReport.id, String).ilike(search_term),
                Batch.batch_code.ilike(search_term),
            )
        )

    total = query.count()

    items = (
        query.order_by(LabReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


def get_all_reports_paginated(db: Session, skip: int, limit: int):
    query = db.query(LabReport)

    total = query.count()

    items = (
        query.order_by(LabReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total