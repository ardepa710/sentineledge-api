from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommandCreate(BaseModel):
    agent_id: str
    type: str = "powershell"
    payload: str
    timeout: int = 300

class CommandResponse(BaseModel):
    job_id: str
    status: str = "pending"
    message: str = "Comando encolado exitosamente"

class CommandResult(BaseModel):
    job_id: str
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None
    finished_at: datetime

class CommandStatus(BaseModel):
    job_id: str
    status: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True