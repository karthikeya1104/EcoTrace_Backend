from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    transporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)

    fuel_type = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=True)
    transport_emission = Column(Float, nullable=False)

    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("Batch")
