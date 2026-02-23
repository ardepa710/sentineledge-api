from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime


from app.models.agent import Agent
from app.models.tenant import Tenant
from app.schemas.agent import AgentRegister
from app.core.security import generate_token, generate_id

async def register_agent(db: AsyncSession, data: AgentRegister):
    """Registra un nuevo agente o actualiza uno existente"""

    # Verificar que el tenant existe y el api_key es válido
    result = await db.execute(
        select(Tenant).where(
            Tenant.id == data.tenant_id,
            Tenant.api_key == data.api_key,
            Tenant.active == True
        )
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        return None, "Tenant no encontrado o API key inválido"

    # Ver si ya existe un agente con este hostname para este tenant
    result = await db.execute(
        select(Agent).where(
            Agent.tenant_id == data.tenant_id,
            Agent.hostname == data.hostname
        )
    )
    existing_agent = result.scalar_one_or_none()

    if existing_agent:
        # Actualizar el agente existente con nueva versión
        existing_agent.os = data.os
        existing_agent.version = data.version
        existing_agent.online = True
        existing_agent.last_seen = datetime.utcnow()
        await db.commit()
        return existing_agent, None

    # Crear nuevo agente
    token = generate_token()
    agent = Agent(
        id=generate_id(),
        tenant_id=data.tenant_id,
        hostname=data.hostname,
        os=data.os,
        version=data.version,
        token=token,
        online=True,
        last_seen=datetime.utcnow()
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent, None

async def get_agents(db: AsyncSession, tenant_id: str):
    """Lista todos los agentes de un tenant"""
    result = await db.execute(
        select(Agent).where(Agent.tenant_id == tenant_id)
    )
    return result.scalars().all()

async def heartbeat(db: AsyncSession, agent_id: str, token: str):
    """Actualiza el último contacto del agente"""
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.token == token
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        return False

    agent.online = True
    agent.last_seen = datetime.utcnow()
    await db.commit()
    return True