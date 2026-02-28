from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs")
async def list_logs(
    tenant_id: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.services.audit_service import get_logs
        logs = await get_logs(db, tenant_id, limit)
        return [
            {
                "id":         l.id,
                "action":     l.action,
                "agent_id":   l.agent_id,
                "hostname":   l.hostname,
                "detail":     l.detail,
                "status":     l.status,
                "created_at": l.created_at
            }
            for l in logs
        ]
    except Exception as e:
        return {"error": str(e)}