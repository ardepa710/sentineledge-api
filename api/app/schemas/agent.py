from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentRegister(BaseModel):
    """Lo que el agente manda al registrarse"""
    hostname: str
    os: str
    version: str
    tenant_id: str
    api_key: str           # el agente se identifica con el api_key del tenant

class AgentResponse(BaseModel):
    """Lo que el servidor responde al registrarse"""
    id: str
    token: str             # token único para este agente
    message: str = "Agente registrado exitosamente"

class AgentInfo(BaseModel):
    """Info del agente para listar"""
    id: str
    hostname: str
    os: str
    version: str
    online: bool
    last_seen: Optional[datetime]

    class Config:
        from_attributes = True