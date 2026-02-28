import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.inventory import (
    AgentInventory, AgentInventoryCPU, AgentInventoryRAM,
    AgentInventoryBIOS, AgentInventoryComputer, AgentInventorySerial,
    AgentInventoryDisk, AgentInventoryNIC, AgentInventoryNICIP,
    AgentInventorySoftware
)
from app.models.agent import Agent


def clean_nulls(obj):
    if isinstance(obj, str):
        return obj.replace("\x00", "").replace("\u0000", "")
    elif isinstance(obj, dict):
        return {k: clean_nulls(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nulls(i) for i in obj]
    return obj


async def save_inventory(db: AsyncSession, data: dict, token: str) -> tuple:
    # Verificar agente
    result = await db.execute(
        select(Agent).where(Agent.id == data["agent_id"], Agent.token == token)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        return None, "Agent not found or invalid token"

    data = clean_nulls(data)

    # Buscar inventory existente
    existing = await db.execute(
        select(AgentInventory).where(AgentInventory.agent_id == agent.id)
    )
    inv = existing.scalar_one_or_none()

    if inv:
        # Eliminar registros hijo — cascade los borra
        await db.delete(inv)
        await db.flush()

    # Crear inventory header
    inv = AgentInventory(
        id           = str(uuid.uuid4()),
        agent_id     = agent.id,
        tenant_id    = agent.tenant_id,
        hostname     = data.get("hostname", ""),
        os           = data.get("os", ""),
        collected_at = datetime.utcnow(),
    )
    db.add(inv)
    await db.flush()  # obtener inv.id

    # CPU
    cpu_data = data.get("cpu") or {}
    db.add(AgentInventoryCPU(
        id              = str(uuid.uuid4()),
        inventory_id    = inv.id,
        name            = cpu_data.get("name", ""),
        number_of_cores = cpu_data.get("number_of_cores", 0),
    ))

    # RAM
    ram_data = data.get("ram") or {}
    db.add(AgentInventoryRAM(
        id                       = str(uuid.uuid4()),
        inventory_id             = inv.id,
        total_physical_memory_gb = ram_data.get("total_physical_memory_gb", 0.0),
    ))

    # BIOS
    bios_data = data.get("bios") or {}
    db.add(AgentInventoryBIOS(
        id                  = str(uuid.uuid4()),
        inventory_id        = inv.id,
        smbios_bios_version = bios_data.get("smbios_bios_version", ""),
        manufacturer        = bios_data.get("manufacturer", ""),
    ))

    # Computer
    comp_data = data.get("computer") or {}
    db.add(AgentInventoryComputer(
        id           = str(uuid.uuid4()),
        inventory_id = inv.id,
        manufacturer = comp_data.get("manufacturer", ""),
        model        = comp_data.get("model", ""),
    ))

    # Serial
    serial_data = data.get("serial") or {}
    db.add(AgentInventorySerial(
        id            = str(uuid.uuid4()),
        inventory_id  = inv.id,
        serial_number = serial_data.get("serial_number", ""),
    ))

    # Disks
    for disk in data.get("disks") or []:
        db.add(AgentInventoryDisk(
            id           = str(uuid.uuid4()),
            inventory_id = inv.id,
            device_id    = disk.get("device_id", ""),
            size_gb      = disk.get("size_gb", 0.0),
            free_gb      = disk.get("free_gb", 0.0),
        ))

    # NICs
    for nic in data.get("nics") or []:
        nic_id = str(uuid.uuid4())
        db.add(AgentInventoryNIC(
            id           = nic_id,
            inventory_id = inv.id,
            description  = nic.get("description", ""),
            mac_address  = nic.get("mac_address", ""),
        ))
        for ip in nic.get("ip_addresses") or []:
            db.add(AgentInventoryNICIP(
                id         = str(uuid.uuid4()),
                nic_id     = nic_id,
                ip_address = ip,
            ))

    # Software
    for sw in data.get("software") or []:
        db.add(AgentInventorySoftware(
            id           = str(uuid.uuid4()),
            inventory_id = inv.id,
            name         = sw.get("name", ""),
            version      = sw.get("version", ""),
            publisher    = sw.get("publisher", ""),
            install_date = sw.get("install_date", ""),
        ))

    await db.commit()
    return inv, None


async def get_inventory(db: AsyncSession, agent_id: str):
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
    return result.scalar_one_or_none()