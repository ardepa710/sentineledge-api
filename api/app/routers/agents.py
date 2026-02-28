from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.schemas.agent import AgentRegister, AgentResponse, AgentInfo
from app.services.agent_service import register_agent, get_agents, heartbeat

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/register", response_model=AgentResponse)
async def register(data: AgentRegister, db: AsyncSession = Depends(get_db)):
    agent, error = await register_agent(db, data)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return AgentResponse(id=agent.id, token=agent.token)

@router.get("")
async def list_agents(tenant_id: str, db: AsyncSession = Depends(get_db)):
    agents = await get_agents(db, tenant_id)
    return [
        {
            "agent_id": a.id,
            "hostname": a.hostname,
            "os": a.os,
            "online": a.online,
            "last_seen": a.last_seen
        }
        for a in agents
    ]

@router.post("/{agent_id}/heartbeat")
async def heartbeat_endpoint(
    agent_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token required")
    token = authorization.replace("Bearer ", "")
    success = await heartbeat(db, agent_id, token)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"status": "ok"}