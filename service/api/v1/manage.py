import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from db import schemas
from db.crud.proxies import create_service, stop_service, restart_service, get_proxy_configs, get_proxy_config, \
    create_proxy_config, get_proxy_unit, get_proxy_units
from service.dependencies import get_db
from utils.utils import get_my_ip, get_my_country_code, get_local_ip

router = APIRouter(prefix="/manage")

logger = logging.getLogger(__name__)


class Host(BaseModel):
    expose_ip: str
    country_code: str
    vlan_ip: str


def parse_configs(config_name):
    if config_name == "all":
        names = None
    else:
        names = [config_name]
    return names


@router.get("/proxy_configs/", response_model=list[schemas.ProxyConfig])
async def fetch_proxy_configs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    proxy_configs = get_proxy_configs(db, skip=skip, limit=limit)
    return proxy_configs


@router.get("/proxy_configs/{config_name}", response_model=schemas.ProxyConfig)
async def fetch_proxy_config(config_name: str, db: Session = Depends(get_db)):
    proxy_configs = get_proxy_config(db, config_name)
    return proxy_configs


@router.post("/proxy_configs/", response_model=schemas.ProxyConfig)
def create_proxy_config(proxy_config: schemas.ProxyConfigCreate, db: Session = Depends(get_db)):
    db_proxy_config = get_proxy_config(db, config_name=proxy_config.name)
    if db_proxy_config:
        raise HTTPException(status_code=400, detail="Config name already registered")
    return create_proxy_config(db=db, proxy_config=proxy_config)


@router.get("/proxies/", tags=["units manage"],
            description="get proxy info by config name")
async def get_proxies(db: Session = Depends(get_db)):
    return [unit.__str__() for unit in get_proxy_units(db)]


@router.get("/proxies/{config_name}", tags=["units manage"],
            description="get proxy info by config name")
async def get_proxy(config_name: str, db: Session = Depends(get_db)):
    return get_proxy_unit(db, config_name=config_name).__str__()


@router.post("/proxies/start/{config_name}", tags=["units manage"],
             description="start proxy by config name")
async def start_proxy(background_tasks: BackgroundTasks, config_name: str, db: Session = Depends(get_db)):
    db_proxy_config = get_proxy_config(db, config_name)
    if not db_proxy_config:
        raise HTTPException(status_code=404, detail="Config not found")
    background_tasks.add_task(create_service, db_proxy_config)
    return db_proxy_config


@router.delete("/proxies/stop/{config_name}", tags=["units manage"], response_model=schemas.ProxyConfig,
               description="stop proxy by config name")
async def stop_proxy(background_tasks: BackgroundTasks, config_name: str, db: Session = Depends(get_db)):
    db_proxy_config = get_proxy_config(db, config_name)
    if not db_proxy_config:
        raise HTTPException(status_code=404, detail="Config not found")
    background_tasks.add_task(stop_service, db_proxy_config)
    return db_proxy_config


@router.put("/proxies/restart/{config_name}", tags=["units manage"], response_model=schemas.ProxyConfig,
            description="restart proxy by config name")
async def restart_proxy(background_tasks: BackgroundTasks, config_name: str, db: Session = Depends(get_db)):
    db_proxy_config = get_proxy_config(db, config_name)
    if not db_proxy_config:
        raise HTTPException(status_code=404, detail="Config not found")
    background_tasks.add_task(restart_service, db_proxy_config)
    return db_proxy_config


@router.get("/host", tags=["manage"], response_model=Host)
async def get_host():
    host_ip = get_my_ip()
    host_country_code = get_my_country_code()
    local_ip = get_local_ip()
    return {
        "expose_ip": host_ip,
        "country_code": host_country_code,
        "vlan_ip": local_ip,
    }
