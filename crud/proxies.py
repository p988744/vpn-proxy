import logging

from utils.proxy_unit import get_proxy_units

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_services(config_name='all'):
    if config_name == 'all':
        config_name = None
    for unit in get_proxy_units(name=config_name):
        logger.info(f"create service {unit.name}")
        unit.start_service()
    return [unit.__str__() for unit in get_proxy_units(name=config_name)]


def stop_services(config_name='all'):
    if config_name == 'all':
        config_name = None
    for unit in get_proxy_units(name=config_name):
        logger.info(f"stop service {unit.name}")
        unit.stop_service()
    return [unit.__str__() for unit in get_proxy_units(name=config_name)]


def restart_services(config_name='all'):
    if config_name == 'all':
        config_name = None
    for unit in get_proxy_units(name=config_name):
        logger.info(f"restart service {unit.name}")
        unit.restart_service()
    return [unit.__str__() for unit in get_proxy_units(name=config_name)]
