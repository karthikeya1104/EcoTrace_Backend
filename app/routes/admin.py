from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole
from app.crud.lab_report import get_all_reports_admin, get_lab_report_by_id, verify_lab_report, reject_lab_report
from app.crud.admin import get_admin_dashboard

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users", response_model=UserOut)
def create_user_admin(
    user: UserCreate,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.admin))
):
    return create_user(db, user, role)


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    return get_admin_dashboard(db)


@router.get("/reports")
def list_reports(
    skip: int = 0,
    limit: int = 10,
    verified: bool | None = None,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    items, total = get_all_reports_admin(db, skip, limit, verified)

    return {
        "total": total,
        "items": items
    }


@router.get("/reports/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    report = get_lab_report_by_id(db, report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.post("/reports/{report_id}/verify")
def verify_report(
    report_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    return verify_lab_report(db, report_id)


@router.post("/reports/{report_id}/reject")
def reject_report(
    report_id: int,
    reason: str | None = None,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    return reject_lab_report(db, report_id, reason)