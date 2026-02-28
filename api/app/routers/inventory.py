from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.schemas.inventory import InventorySubmit
from app.services.inventory_service import save_inventory, get_inventory

router = APIRouter(prefix="/agents", tags=["Inventory"])

@router.post("/inventory")
async def submit_inventory(
    data: InventorySubmit,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token required")

    token = authorization.replace("Bearer ", "")
    inv, error = await save_inventory(db, data.model_dump(), token)

    if error:
        raise HTTPException(status_code=401, detail=error)

    return {
        "status": "ok",
        "agent_id": inv.agent_id,
        "collected_at": inv.collected_at,
        "software_count": len(data.software),
        "disk_count": len(data.disks),
        "nic_count": len(data.nics),
    }

@router.get("/inventory/{agent_id}")
async def get_agent_inventory(
    agent_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    inv = await get_inventory(db, agent_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inv