from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseSettings
from yaml import Loader

BASE_DIR = Path(__file__).parent


# PROXY_CONFIGS = None


# parse yaml to dict
def parse_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f, Loader=Loader)


class Settings(BaseSettings):
    HOST: Optional[str] = None
    PROXY_USER: Optional[str] = None
    PROXY_PASSWORD: Optional[str] = None
    SURFSHARK_USER: Optional[str] = None
    SURFSHARK_PASSWORD: Optional[str] = None
    CONNECTION_TYPE: str = 'udp'
    CONTAINER_PREFIX: str = 'proxy-'
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

    class Config:
        env_file = '.env'
        strict = True


# create pydantic settings instance with cache
def create_settings():
    return Settings()


settings = create_settings()
