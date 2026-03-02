from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, UniqueConstraint
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
    manufacturing_location = Column(String)
    base_carbon_footprint = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    status = Column(Enum(BatchStatus), default=BatchStatus.pending)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.auto_verified)

    # Relationships
    product = relationship("Product", back_populates="batches")
    lab_reports = relationship("LabReport", back_populates="batch")
    ai_scores = relationship("AIScore", back_populates="batch")
    transports = relationship("Transport", back_populates="batch")

    materials = relationship(
        "BatchMaterial",
        back_populates="batch",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('product_id', 'batch_code', name='uq_product_batch_code'),
    )