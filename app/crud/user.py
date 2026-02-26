from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import hash_password
from fastapi import HTTPException
from app.utils.logger import get_logger

logger = get_logger("crud.user")


def create_user(db: Session, user, role: UserRole = UserRole.consumer):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=role
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.exception("Failed to create user %s", user.email)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
