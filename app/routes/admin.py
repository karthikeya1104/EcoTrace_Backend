from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users", response_model=UserOut)
def create_user_admin(
    user: UserCreate,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.admin))
):
    return create_user(db, user, role)