from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.database import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    consumer = "consumer"
    manufacturer = "manufacturer"
    transporter = "transporter"
    lab = "lab"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
