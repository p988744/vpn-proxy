from sqlalchemy import Boolean, Column, Integer, String, DateTime, func

from .database import Base


class ProxyConfig(Base):
    __tablename__ = "proxy_config"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    connection_type = Column(String, nullable=False, default="udp")
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    expose_port = Column(Integer, nullable=False, index=True, unique=True)
    is_active = Column(Boolean, default=True)
    status = Column(String, nullable=True, default="NOT_STARTED")
    created_at = Column(DateTime(timezone=True), server_default=func.now(tz='Asia/Taipei'))
    updated_at = Column(DateTime(timezone=True), on_update=func.now(tz='Asia/Taipei'), nullable=True)
