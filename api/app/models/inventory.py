from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AgentInventory(Base):
    __tablename__ = "agent_inventory"

    id           = Column(String, primary_key=True)
    agent_id     = Column(String, ForeignKey("agents.id"), nullable=False, unique=True)
    tenant_id    = Column(String, nullable=False)
    hostname     = Column(String, nullable=True)
    os           = Column(String, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)

    cpu      = relationship("AgentInventoryCPU",      back_populates="inventory", uselist=False, cascade="all, delete-orphan")
    ram      = relationship("AgentInventoryRAM",      back_populates="inventory", uselist=False, cascade="all, delete-orphan")
    bios     = relationship("AgentInventoryBIOS",     back_populates="inventory", uselist=False, cascade="all, delete-orphan")
    computer = relationship("AgentInventoryComputer", back_populates="inventory", uselist=False, cascade="all, delete-orphan")
    serial   = relationship("AgentInventorySerial",   back_populates="inventory", uselist=False, cascade="all, delete-orphan")
    disks    = relationship("AgentInventoryDisk",     back_populates="inventory", cascade="all, delete-orphan")
    nics     = relationship("AgentInventoryNIC",      back_populates="inventory", cascade="all, delete-orphan")
    software = relationship("AgentInventorySoftware", back_populates="inventory", cascade="all, delete-orphan")


class AgentInventoryCPU(Base):
    __tablename__ = "agent_inventory_cpu"

    id             = Column(String, primary_key=True)
    inventory_id   = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    name           = Column(String, nullable=True)
    number_of_cores = Column(Integer, nullable=True)

    inventory = relationship("AgentInventory", back_populates="cpu")


class AgentInventoryRAM(Base):
    __tablename__ = "agent_inventory_ram"

    id                      = Column(String, primary_key=True)
    inventory_id            = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    total_physical_memory_gb = Column(Float, nullable=True)

    inventory = relationship("AgentInventory", back_populates="ram")


class AgentInventoryBIOS(Base):
    __tablename__ = "agent_inventory_bios"

    id                  = Column(String, primary_key=True)
    inventory_id        = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    smbios_bios_version = Column(String, nullable=True)
    manufacturer        = Column(String, nullable=True)

    inventory = relationship("AgentInventory", back_populates="bios")


class AgentInventoryComputer(Base):
    __tablename__ = "agent_inventory_computer"

    id           = Column(String, primary_key=True)
    inventory_id = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    manufacturer = Column(String, nullable=True)
    model        = Column(String, nullable=True)

    inventory = relationship("AgentInventory", back_populates="computer")


class AgentInventorySerial(Base):
    __tablename__ = "agent_inventory_serial"

    id            = Column(String, primary_key=True)
    inventory_id  = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    serial_number = Column(String, nullable=True)

    inventory = relationship("AgentInventory", back_populates="serial")


class AgentInventoryDisk(Base):
    __tablename__ = "agent_inventory_disks"

    id           = Column(String, primary_key=True)
    inventory_id = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    device_id    = Column(String, nullable=True)
    size_gb      = Column(Float, nullable=True)
    free_gb      = Column(Float, nullable=True)

    inventory = relationship("AgentInventory", back_populates="disks")


class AgentInventoryNIC(Base):
    __tablename__ = "agent_inventory_nics"

    id           = Column(String, primary_key=True)
    inventory_id = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    description  = Column(String, nullable=True)
    mac_address  = Column(String, nullable=True)

    inventory   = relationship("AgentInventory", back_populates="nics")
    ip_addresses = relationship("AgentInventoryNICIP", back_populates="nic", cascade="all, delete-orphan")


class AgentInventoryNICIP(Base):
    __tablename__ = "agent_inventory_nic_ips"

    id         = Column(String, primary_key=True)
    nic_id     = Column(String, ForeignKey("agent_inventory_nics.id"), nullable=False)
    ip_address = Column(String, nullable=True)

    nic = relationship("AgentInventoryNIC", back_populates="ip_addresses")


class AgentInventorySoftware(Base):
    __tablename__ = "agent_inventory_software"

    id           = Column(String, primary_key=True)
    inventory_id = Column(String, ForeignKey("agent_inventory.id"), nullable=False)
    name         = Column(String, nullable=True)
    version      = Column(String, nullable=True)
    publisher    = Column(String, nullable=True)
    install_date = Column(String, nullable=True)

    inventory = relationship("AgentInventory", back_populates="software")