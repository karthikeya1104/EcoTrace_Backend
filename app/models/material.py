from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from app.database import Base
import enum

class BatchMaterial(Base):
    __tablename__ = "batch_materials"

    id = Column(Integer, primary_key=True)

    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"))
    material_id = Column(Integer, ForeignKey("materials.id"))

    percentage = Column(Float)
    source_info_provided = Column(Boolean, default=False)
    source = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("batch_id", "material_id", name="uq_batch_material"),
    )

    # Relationships
    batch = relationship("Batch", back_populates="materials")
    material = relationship("Material", back_populates="batch_materials")


class RiskLevel(enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False)
    common_name = Column(String)
    risk_level = Column(Enum(RiskLevel))
    description = Column(String)

    #  REQUIRED RELATIONSHIP
    batch_materials = relationship(
        "BatchMaterial",
        back_populates="material"
    )