from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.schemas.inventory import InventorySubmit
from app.services.inventory_service import save_inventory, get_inventory
from app.models.inventory import (
    AgentInventory, AgentInventoryCPU, AgentInventoryRAM,
    AgentInventoryBIOS, AgentInventoryComputer, AgentInventorySerial,
    AgentInventoryDisk, AgentInventoryNIC, AgentInventoryNICIP,
    AgentInventorySoftware
)
from app.models.agent import Agent
from sqlalchemy.orm import selectinload

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
async def get_agent_inventory(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentInventory)
        .where(AgentInventory.agent_id == agent_id)
        .options(
            selectinload(AgentInventory.cpu),
            selectinload(AgentInventory.ram),
            selectinload(AgentInventory.bios),
            selectinload(AgentInventory.computer),
            selectinload(AgentInventory.serial),
            selectinload(AgentInventory.disks),
            selectinload(AgentInventory.nics).selectinload(AgentInventoryNIC.ip_addresses),
            selectinload(AgentInventory.software),
        )
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return {
        "agent_id": inv.agent_id,
        "hostname": inv.hostname,
        "os": inv.os,
        "collected_at": inv.collected_at,
        "cpu": {"name": inv.cpu.name, "number_of_cores": inv.cpu.number_of_cores} if inv.cpu else None,
        "ram": {"total_physical_memory_gb": inv.ram.total_physical_memory_gb} if inv.ram else None,
        "bios": {"smbios_bios_version": inv.bios.smbios_bios_version, "manufacturer": inv.bios.manufacturer} if inv.bios else None,
        "computer": {"manufacturer": inv.computer.manufacturer, "model": inv.computer.model} if inv.computer else None,
        "serial": {"serial_number": inv.serial.serial_number} if inv.serial else None,
        "disks": [{"device_id": d.device_id, "size_gb": d.size_gb, "free_gb": d.free_gb} for d in inv.disks],
        "nics": [
            {
                "description": n.description,
                "mac_address": n.mac_address,
                "ip_addresses": [ip.ip_address for ip in n.ip_addresses]
            }
            for n in inv.nics
        ],
        "software": [
            {"name": s.name, "version": s.version, "publisher": s.publisher, "install_date": s.install_date}
            for s in inv.software
        ],
    }


@router.get("/software/search")
async def search_software(q: str, db: AsyncSession = Depends(get_db)):
    """Busca qué agentes tienen un software específico"""
    result = await db.execute(
        select(AgentInventorySoftware, AgentInventory, Agent)
        .join(AgentInventory, AgentInventory.id == AgentInventorySoftware.inventory_id)
        .join(Agent, Agent.id == AgentInventory.agent_id)
        .where(AgentInventorySoftware.name.ilike(f"%{q}%"))
        .order_by(AgentInventorySoftware.name)
    )
    rows = result.all()
    return [
        {
            "agent_id": agent.id,
            "hostname": agent.hostname,
            "software_name": sw.name,
            "version": sw.version,
            "publisher": sw.publisher,
            "install_date": sw.install_date,
        }
        for sw, inv, agent in rows
    ]