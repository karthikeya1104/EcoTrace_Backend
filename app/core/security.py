from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.database import SessionLocal
from app.models.user import User

# ---------- JWT Settings ----------
SECRET_KEY = "CHANGE_ME_IN_ENV"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_DAYS = 30
REFRESH_TOKEN_EXPIRE_DAYS = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Password ----------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ---------- Token Core ----------
def _create_token(data: dict, expires_delta: timedelta):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int, role: str):
    return _create_token(
        {
            "sub": str(user_id),
            "role": role,
            "type": "access",
        },
        timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    )


def create_refresh_token(user_id: int):
    return _create_token(
        {
            "sub": str(user_id),
            "type": "refresh",
        },
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, token_type: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------- Current User Dependency ----------
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token, token_type="access")

    db = SessionLocal()
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
