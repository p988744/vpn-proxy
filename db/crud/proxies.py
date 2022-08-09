import logging

from sqlalchemy.orm import Session

from db import models, schemas
from settings import settings
from utils.proxy_unit import ProxyUnit

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_unit_config(config):
    return {
        "surfshark_user": settings.SURFSHARK_USER,
        "surfshark_password": settings.SURFSHARK_PASSWORD,
        "country": config.get('country'),
        "city": config.get('city'),
        "connection_type": settings.CONNECTION_TYPE,
        "expose_port": config.get('expose_port'),
    }


#
# def check_configs(names: List) -> dict:
#     units_conf = settings.get_proxy_configs()
#     if names is None:
#         return units_conf
#     return {name: units_conf.get(name) for name in names}


def get_proxy_config(db: Session, config_name: str):
    return db.query(models.ProxyConfig).filter(models.ProxyConfig.name == config_name).first()


def get_proxy_config_by_id(db: Session, config_id: str):
    return db.query(models.ProxyConfig).filter(models.ProxyConfig.id == config_id).first()


def get_proxy_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ProxyConfig).offset(skip).limit(limit).all()


def create_proxy_config(db: Session, proxy_config: schemas.ProxyConfigCreate):
    db_config = models.ProxyConfig(**proxy_config.dict(exclude_unset=True))
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_proxy_unit(db: Session, config_name: str):
    db_config = get_proxy_config(db, config_name)
    if db_config is None:
        return None
    db_config = schemas.ProxyConfig.from_orm(db_config)
    unit_config = parse_unit_config(db_config.dict())
    return ProxyUnit(db_config.name, **unit_config)


def get_proxy_units(db: Session):
    db_configs: list[models.ProxyConfig] = db.query(models.ProxyConfig).all()
    for db_config in db_configs:
        db_config = schemas.ProxyConfig.from_orm(db_config)
        unit_config = parse_unit_config(db_config.dict())
        yield ProxyUnit(db_config.name, **unit_config)


def create_service(proxy_config: models.ProxyConfig):
    proxy_config = schemas.ProxyConfig.from_orm(proxy_config)
    unit_config = parse_unit_config(proxy_config.dict())
    logger.info(f"create service {proxy_config.name}")
    unit = ProxyUnit(proxy_config.name, **unit_config)
    unit.start_service()
    return unit.__str__()


def stop_service(proxy_config: models.ProxyConfig):
    proxy_config = schemas.ProxyConfig.from_orm(proxy_config)
    unit_config = parse_unit_config(proxy_config.dict())
    logger.info(f"stop service {proxy_config.name}")
    unit = ProxyUnit(proxy_config.name, **unit_config)
    unit.stop_service()
    return unit.__str__()


def restart_service(proxy_config: models.ProxyConfig):
    proxy_config = schemas.ProxyConfig.from_orm(proxy_config)
    unit_config = parse_unit_config(proxy_config.dict())
    logger.info(f"restart service {proxy_config.name}")
    unit = ProxyUnit(proxy_config.name, **unit_config)
    unit.restart_service()
    return unit.__str__()
