from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id         = Column(String, primary_key=True)
    tenant_id  = Column(String, nullable=False)
    agent_id   = Column(String, nullable=True)
    hostname   = Column(String, nullable=True)
    action     = Column(String, nullable=False)
    detail     = Column(Text, nullable=True)
    status     = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)