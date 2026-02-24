from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from app.database import Base
from datetime import datetime

class AIScore(Base):
    __tablename__ = "ai_scores"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))

    environment_score = Column(Float)
    ethics_score = Column(Float)
    safety_score = Column(Float)
    cost_score = Column(Float)
    final_score = Column(Float)

    reasoning = Column(String)

    generated_at = Column(DateTime, default=datetime.utcnow)
