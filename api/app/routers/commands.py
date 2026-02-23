from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.command import CommandCreate, CommandResponse, CommandResult, CommandStatus
from app.services.command_service import (
    create_command,
    get_pending_commands,
    save_result,
    get_command_status
)

router = APIRouter(prefix="/commands", tags=["Comandos"])

@router.post("", response_model=CommandResponse)
async def create_command_endpoint(
    data: CommandCreate,
    db: AsyncSession = Depends(get_db)
):
    command, error = await create_command(db, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return CommandResponse(job_id=command.id)

@router.post("/result")
async def save_result_endpoint(
    data: CommandResult,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.replace("Bearer ", "")
    success, error = await save_result(db, token, data)
    if not success:
        raise HTTPException(status_code=400, detail=error)
    return {"status": "ok"}

@router.get("/status/{job_id}", response_model=CommandStatus)
async def get_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    command = await get_command_status(db, job_id)
    if not command:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    # Mapear id → job_id manualmente
    return CommandStatus(
        job_id=command.id,
        status=command.status,
        exit_code=command.exit_code,
        stdout=command.stdout,
        stderr=command.stderr,
        error=command.error,
        created_at=command.created_at,
        finished_at=command.finished_at
    )

@router.get("/pending/{agent_id}")
async def get_pending(
    agent_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.replace("Bearer ", "")
    commands, error = await get_pending_commands(db, agent_id, token)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return commands