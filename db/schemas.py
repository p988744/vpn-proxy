import datetime
from typing import Optional

from pydantic import BaseModel


class ProxyConfigBase(BaseModel):
    name: str
    connection_type: str = "udp"
    country: str
    city: str
    expose_port: int


class ProxyConfigCreate(ProxyConfigBase):
    pass


class ProxyConfigUpdate(ProxyConfigBase):
    is_active: Optional[bool]
    status: Optional[str]


class ProxyConfig(ProxyConfigBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    status: str = "NOT_STARTED"

    class Config:
        orm_mode = True
