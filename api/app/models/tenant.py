from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Tenant(Base):
    """Representa un cliente MSP"""
    __tablename__ = "tenants"

    id       = Column(String, primary_key=True)  # ej: "cliente-abc"
    name     = Column(String, nullable=False)
    api_key  = Column(String, unique=True, nullable=False)
    active   = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Un tenant tiene muchos agentes
    agents = relationship("Agent", back_populates="tenant")