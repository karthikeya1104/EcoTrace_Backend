from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class AIScore(Base):
    __tablename__ = "ai_scores"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))

    rating = Column(Float, nullable=False) # Overall rating from 1 to 5

    reasoning = Column(String)

    generated_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("Batch", back_populates="ai_scores")