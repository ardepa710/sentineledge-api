from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Command(Base):
    """Representa un comando/job enviado a un agente"""
    __tablename__ = "commands"

    id         = Column(String, primary_key=True)   # UUID del job
    agent_id   = Column(String, ForeignKey("agents.id"), nullable=False)
    type       = Column(String, nullable=False)      # "powershell", "bash"
    payload    = Column(Text, nullable=False)         # el script
    timeout    = Column(Integer, default=300)         # segundos
    status     = Column(String, default="pending")   # pending/running/completed/failed
    exit_code  = Column(Integer)
    stdout     = Column(Text)
    stderr     = Column(Text)
    error      = Column(Text)
    created_at  = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime)

    agent = relationship("Agent", back_populates="commands")