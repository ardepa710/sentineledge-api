from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import httpx

from app.models.command import Command
from app.models.agent import Agent
from app.schemas.command import CommandCreate, CommandResult
from app.core.security import generate_id
from app.core.config import settings

async def create_command(db: AsyncSession, data: CommandCreate):
    """Crea un comando pendiente para un agente"""

    # Verificar que el agente existe
    result = await db.execute(
        select(Agent).where(Agent.id == data.agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        return None, "Agente no encontrado"

    if not agent.online:
        return None, "Agente está offline"

    command = Command(
        id=generate_id(),
        agent_id=data.agent_id,
        type=data.type,
        payload=data.payload,
        timeout=data.timeout,
        status="pending"
    )
    db.add(command)
    await db.commit()
    await db.refresh(command)

    return command, None

async def get_pending_commands(db: AsyncSession, agent_id: str, token: str):
    """El agente solicita sus comandos pendientes"""

    # Validar token del agente
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.token == token
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        return None, "Token inválido"

    # Obtener comandos pendientes
    result = await db.execute(
        select(Command).where(
            Command.agent_id == agent_id,
            Command.status == "pending"
        )
    )
    commands = result.scalars().all()

    # Marcarlos como "running"
    for cmd in commands:
        cmd.status = "running"
    await db.commit()

    return commands, None

async def save_result(db: AsyncSession, token: str, data: CommandResult):
    """Guarda el resultado reportado por el agente"""

    # Buscar el comando
    result = await db.execute(
        select(Command).where(Command.id == data.job_id)
    )
    command = result.scalar_one_or_none()

    if not command:
        return False, "Job not found"

    # Verificar que el token corresponde al agente dueño del comando
    agent_result = await db.execute(
        select(Agent).where(
            Agent.id == command.agent_id,
            Agent.token == token
        )
    )
    agent = agent_result.scalar_one_or_none()

    if not agent:
        return False, "Invalid Token"

    # Guardar resultado
    command.status = "completed" if data.exit_code == 0 else "failed"
    command.exit_code = data.exit_code
    command.stdout = data.stdout
    command.stderr = data.stderr
    command.error = data.error
    command.finished_at = data.finished_at.replace(tzinfo=None)
    await db.commit()

    # Disparar webhook a N8N si está configurado
    if settings.N8N_WEBHOOK_BASE_URL:
        await notify_n8n(command, agent)

    return True, None

async def get_command_status(db: AsyncSession, job_id: str):
    """Retrieve state of a job — para N8N by polling"""
    result = await db.execute(
        select(Command).where(Command.id == job_id)
    )
    return result.scalar_one_or_none()

async def notify_n8n(command: Command, agent: Agent):
    """Send result to N8N via webhook"""
    webhook_url = f"{settings.N8N_WEBHOOK_BASE_URL}/webhook/agent-result"

    payload = {
        "job_id": command.id,
        "agent_id": agent.id,
        "hostname": agent.hostname,
        "status": command.status,
        "exit_code": command.exit_code,
        "stdout": command.stdout,
        "stderr": command.stderr,
        "finished_at": command.finished_at.isoformat() if command.finished_at else None
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        # No fallar si N8N no está disponible
        print(f"Warning: N8N not available: {e}")