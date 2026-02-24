from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class BatchStatus(enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"
    
class ValidationStatus(enum.Enum):
    auto_verified = "auto_verified"
    ai_review = "ai_review"
    lab_required = "lab_required"

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    batch_code = Column(String, nullable=False)
    manufacture_date = Column(DateTime)
    expiry_date = Column(DateTime)
    material_info = Column(JSON)   # list of materials
    material_source = Column(String, nullable=True)
    manufacturing_location = Column(String)
    base_carbon_footprint = Column(Float)
    qr_payload  = Column(String)
    status = Column(Enum(BatchStatus), default=BatchStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.ai_review)
    
    product = relationship("Product", back_populates="batches")
    lab_reports = relationship("LabReport", back_populates="batch")
    
    __table_args__ = (
        UniqueConstraint('product_id', 'batch_code', name='uq_product_batch_code'),
    )
