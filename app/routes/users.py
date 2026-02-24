from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserOut, UserUpdate
from app.crud.user import get_user, get_users, update_user, delete_user
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Prevent users from updating their own role
    if user_update.role is not None and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Cannot update role")
    return update_user(db, current_user.id, user_update)

@router.get("/", response_model=list[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.admin))
):
    return get_users(db, skip, limit)

@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Allow users to view their own info, admins to view any
    if current_user.id != user_id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.admin))
):
    return update_user(db, user_id, user_update)

@router.delete("/{user_id}")
def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.admin))
):
    return delete_user(db, user_id)