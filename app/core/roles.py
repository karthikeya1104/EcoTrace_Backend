from fastapi import Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import UserRole

def require_role(required: UserRole):
    def checker(user = Depends(get_current_user)):
        if user.role != required and user.role != UserRole.admin:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return checker
