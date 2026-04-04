from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("batch_id", "user_id", name="uq_user_batch_review"),
    )

    # in Review model
    user = relationship("User")
    batch = relationship("Batch")