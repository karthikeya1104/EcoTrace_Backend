from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(Integer, ForeignKey("batches.id"))
    lab_id = Column(Integer, ForeignKey("users.id"))

    test_summary = Column(String)
    certifications = Column(String)

    eco_rating = Column(Integer)
    lab_score = Column(Float, nullable=False)

    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 Relationships
    batch = relationship("Batch", back_populates="lab_reports")
    lab = relationship("User")