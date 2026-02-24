from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String)
    entity_id = Column(Integer)
    action = Column(String)
    performed_by = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
