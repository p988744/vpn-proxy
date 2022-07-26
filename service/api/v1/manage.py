import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from crud.proxies import create_services, stop_services, restart_services, get_proxy_units, check_configs
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


@router.get("/proxies/{config_name}", tags=["manage"],
            description="get proxy info by config name, all for all proxies")
async def get_proxy(names=Depends(parse_configs)):
    return [unit.__str__() for name, unit in get_proxy_units(names=names)]


@router.post("/proxies/start/{config_name}", tags=["manage"],
             description="start proxy by config name, all for all proxies")
async def start_proxy(background_tasks: BackgroundTasks, names=Depends(parse_configs)):
    background_tasks.add_task(create_services, names)
    return {name: config if config else 'config not found' for name, config in check_configs(names).items()}


@router.delete("/proxies/stop/{config_name}", tags=["manage"],
               description="stop proxy by config name, all for all proxies")
async def stop_proxy(background_tasks: BackgroundTasks, names=Depends(parse_configs)):
    background_tasks.add_task(stop_services, names)
    return {name: config if config else 'config not found' for name, config in check_configs(names).items()}


@router.put("/proxies/restart/{config_name}", tags=["manage"],
            description="restart proxy by config name, all for all proxies")
async def restart_proxy(background_tasks: BackgroundTasks, names=Depends(parse_configs)):
    background_tasks.add_task(restart_services, names)
    return {name: config if config else 'config not found' for name, config in check_configs(names).items()}


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
