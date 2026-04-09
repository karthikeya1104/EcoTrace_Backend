from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class SafetyStatus(enum.Enum):
    safe = "safe"
    caution = "caution"
    unsafe = "unsafe"


class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(Integer, ForeignKey("batches.id"))
    lab_id = Column(Integer, ForeignKey("users.id"))

    analysis_data = Column(JSON)
    certifications = Column(String)

    safety_status = Column(Enum(SafetyStatus))

    notes = Column(String)

    lab_score = Column(Float, nullable=False) # Rating from 1 to 5

    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    #  Relationships
    batch = relationship("Batch", back_populates="lab_reports")
    lab = relationship("User")