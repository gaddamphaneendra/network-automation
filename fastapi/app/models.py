from pydantic import BaseModel
from typing import List, Optional


class Device(BaseModel):
    device_type: str
    ip: str
    username: str
    password: str
    secret: Optional[str] = None


class HealthCheckRequest(BaseModel):
    devices: List[Device]


class BackupRequest(BaseModel):
    devices: List[Device]
