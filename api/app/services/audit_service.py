import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def log(
    db: AsyncSession,
    tenant_id: str,
    action: str,
    agent_id: str = None,
    hostname: str = None,
    detail: str = None,
    status: str = "success"
):
    try:
        from app.models.audit import AuditLog
        entry = AuditLog(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            agent_id=agent_id,
            hostname=hostname,
            action=action,
            detail=detail,
            status=status,
            created_at=datetime.utcnow()
        )
        db.add(entry)
        await db.commit()
    except Exception as e:
        pass  # No romper el flujo principal si falla el audit log

async def get_logs(db: AsyncSession, tenant_id: str, limit: int = 100):
    from app.models.audit import AuditLog
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()