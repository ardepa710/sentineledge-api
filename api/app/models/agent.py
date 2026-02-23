from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Agent(Base):
    """Representa un endpoint con el agente instalado"""
    __tablename__ = "agents"

    id         = Column(String, primary_key=True)  # UUID generado al registrarse
    tenant_id  = Column(String, ForeignKey("tenants.id"), nullable=False)
    hostname   = Column(String, nullable=False)
    os         = Column(String)                    # "windows", "linux"
    version    = Column(String)                    # versión del agente
    token      = Column(String, unique=True)       # token de autenticación
    online     = Column(Boolean, default=False)
    last_seen  = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    tenant   = relationship("Tenant", back_populates="agents")
    commands = relationship("Command", back_populates="agent")