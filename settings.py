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
    PROXY_UNIT_CONFIG_FILE: str = 'proxy_units.yml'

    class Config:
        env_file = '.env'
        strict = True


# create pydantic settings instance with cache
def create_settings():
    return Settings()


def parse_unit_configs():
    with open(settings.PROXY_UNIT_CONFIG_FILE, 'r') as f:
        configs = yaml.load(f, Loader=Loader)
    proxy_units = configs
    return {
        name: {
            "surfshark_user": settings.SURFSHARK_USER,
            "surfshark_password": settings.SURFSHARK_PASSWORD,
            "surfshark_country": unit_conf.get('surfshark_country'),
            "surfshark_city": unit_conf.get('surfshark_city'),
            "connection_type": settings.CONNECTION_TYPE,
            "expose_port": unit_conf.get('expose_port'),
        } for name, unit_conf in proxy_units.items()}


def get_proxy_configs(reload=False) -> Dict:
    global PROXY_CONFIGS
    if reload or PROXY_CONFIGS is None:
        PROXY_CONFIGS = parse_unit_configs()
    return PROXY_CONFIGS


settings = create_settings()
PROXY_CONFIGS = get_proxy_configs(reload=True)

if __name__ == '__main__':
    print(get_proxy_configs(reload=True))
