from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CPUInfo(BaseModel):
    name: str = ""
    number_of_cores: int = 0

class RAMInfo(BaseModel):
    total_physical_memory_gb: float = 0.0

class BIOSInfo(BaseModel):
    smbios_bios_version: str = ""
    manufacturer: str = ""

class ComputerInfo(BaseModel):
    manufacturer: str = ""
    model: str = ""

class SerialInfo(BaseModel):
    serial_number: str = ""

class DiskInfo(BaseModel):
    device_id: str = ""
    size_gb: float = 0.0
    free_gb: float = 0.0

class NICInfo(BaseModel):
    description: str = ""
    mac_address: str = ""
    ip_addresses: List[str] = []

class SoftwareInfo(BaseModel):
    name: str = ""
    version: str = ""
    publisher: str = ""
    install_date: str = ""

class InventorySubmit(BaseModel):
    agent_id: str
    hostname: str = ""
    os: str = ""
    cpu: CPUInfo = CPUInfo()
    ram: RAMInfo = RAMInfo()
    bios: BIOSInfo = BIOSInfo()
    computer: ComputerInfo = ComputerInfo()
    serial: SerialInfo = SerialInfo()
    disks: List[DiskInfo] = []
    nics: List[NICInfo] = []
    software: List[SoftwareInfo] = []