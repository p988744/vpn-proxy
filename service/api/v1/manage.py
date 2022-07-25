import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from crud.proxies import create_services, stop_services, restart_services
from utils.proxy_unit import get_proxy_units
from utils.utils import get_my_ip, get_my_country_code, get_local_ip

router = APIRouter(prefix="/manage")

logger = logging.getLogger(__name__)


class Host(BaseModel):
    expose_ip: str
    country_code: str
    vlan_ip: str


@router.get("/proxies/{config_name}", tags=["manage"],
            description="get proxy info by config name, all for all proxies")
async def get_proxy(config_name: str = "all"):
    return [unit.__str__() for unit in get_proxy_units(name=config_name)]


@router.post("/proxies/start/{config_name}", tags=["manage"],
             description="start proxy by config name, all for all proxies")
async def start_proxy(background_tasks: BackgroundTasks, config_name: str = "all"):
    background_tasks.add_task(create_services, config_name)
    return {'message': f'start proxy {config_name}'}


@router.delete("/proxies/stop/{config_name}", tags=["manage"],
               description="stop proxy by config name, all for all proxies")
async def stop_proxy(background_tasks: BackgroundTasks, config_name: str = 'all'):
    background_tasks.add_task(stop_services, config_name)
    return {'message': f'stop proxy {config_name}'}


@router.put("/proxies/restart/{config_name}", tags=["manage"],
            description="restart proxy by config name, all for all proxies")
async def restart_proxy(background_tasks: BackgroundTasks, config_name: str = "all"):
    background_tasks.add_task(restart_services, config_name)
    return {'message': f'restart proxy {config_name}'}


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
