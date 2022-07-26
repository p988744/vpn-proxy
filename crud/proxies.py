import logging
from typing import List

import settings
from utils.proxy_unit import ProxyUnit

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_configs(names: List) -> dict:
    units_conf = settings.get_proxy_configs()
    if names is None:
        return units_conf
    return {name: units_conf.get(name) for name in names}


def get_proxy_units(names: List = None):
    units_conf = settings.get_proxy_configs()
    if names:
        for name, config in check_configs(names).items():
            if config is None:
                logger.error(f"proxy config {name} not found")
                yield name, None
            else:
                yield name, ProxyUnit(name, **config)
    else:
        for name, unit_conf in units_conf.items():
            yield name, ProxyUnit(name, **unit_conf)


def create_services(config_name_list: List[str] = None):
    for name, unit in get_proxy_units(names=config_name_list):
        if unit is None:
            continue
        logger.info(f"create service {unit.name}")
        unit.start_service()
    return [unit.__str__() for unit in get_proxy_units(names=config_name_list)]


def stop_services(config_name_list: List[str] = None):
    for name, unit in get_proxy_units(names=config_name_list):
        if unit is None:
            continue
        logger.info(f"stop service {unit.name}")
        unit.stop_service()
    return [unit.__str__() for unit in get_proxy_units(names=config_name_list)]


def restart_services(config_name_list: List[str] = None):
    if config_name_list == 'all':
        config_name_list = None
    for name, unit in get_proxy_units(names=config_name_list):
        if unit is None:
            continue
        logger.info(f"restart service {unit.name}")
        unit.restart_service()
    return [unit.__str__() for unit in get_proxy_units(names=config_name_list)]
