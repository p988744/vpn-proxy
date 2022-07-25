import logging
from abc import ABC

import docker

import settings
from utils.docker import docker_client

logger = logging.getLogger(__name__)


def get_proxy_units(name=None):
    units_conf = settings.get_proxy_configs()
    if name and name != 'all':
        config = units_conf.get(name)
        assert config, f"proxy config {name} not found"
        yield ProxyUnit(name, **config)
    else:
        for name, unit_conf in units_conf.items():
            yield ProxyUnit(name, **unit_conf)


class ProxyUnit(ABC):
    base_dir = settings.BASE_DIR
    vpn_image = 'ilteoood/docker-surfshark'
    squid_image = 'sameersbn/squid:3.5.27-2'

    def __init__(self, name, surfshark_user, surfshark_password, surfshark_country='us', surfshark_city='nyc',
                 connection_type='udp', expose_port=3128):
        self.surfshark_user = surfshark_user
        self.surfshark_password = surfshark_password
        self.surfshark_country = surfshark_country
        self.surfshark_city = surfshark_city
        self.connection_type = connection_type
        self.expose_port = expose_port
        self.name = name

        self.vpn_container = self.load_vpn_container()
        self.squid_container = self.load_squid_container()

    def __str__(self):
        return {
            'name': self.name,
            'status': self.status,
            'vpn_container': {
                'id': self.vpn_container.id if self.vpn_container else 'not found',
                'name': self.vpn_container_name,
                'status': self.vpn_container.status if self.vpn_container else 'not found',
            },
            'squid_container': {
                'id': self.squid_container.id if self.squid_container else 'not found',
                'name': self.squid_container_name,
                'status': self.squid_container.status if self.squid_container else 'not found',
            },
            'country': self.surfshark_country,
            'city': self.surfshark_city,
            'expose_port': self.expose_port,
            'connection_type': self.connection_type,
        }

    @property
    def surfshark_config(self):
        return {
            "SURFSHARK_USER": self.surfshark_user,
            "SURFSHARK_PASSWORD": self.surfshark_password,
            "SURFSHARK_COUNTRY": self.surfshark_country,
            "SURFSHARK_CITY": self.surfshark_city,
            "CONNECTION_TYPE": self.connection_type,
        }

    @property
    def vpn_container_name(self):
        return f"{self.name}-vpn-{self.expose_port}"

    @property
    def squid_container_name(self):
        return f"{self.name}-squid-{self.expose_port}"

    @property
    def status(self):
        if self.vpn_container and self.squid_container:
            if self.vpn_container.status == 'running' and self.squid_container.status == 'running':
                return 'ready'
            else:
                return 'stopped'
        else:
            return 'not found'

    # create docker container with name and volume
    def create_vpn_container(self, *, client=None, detach=True,
                             environments=None):
        if client is None:
            client = docker_client
        # name = self.vpn_container_name
        if environments is None:
            environments = self.surfshark_config

        if self.vpn_container is None:
            logger.info("...starting vpn container...")
            container = client.containers.run(image=self.vpn_image, name=self.vpn_container_name,
                                              cap_add=['NET_ADMIN'],
                                              ports={'3128/tcp': self.expose_port},
                                              devices=['/dev/net/tun'], detach=detach,
                                              dns=['surfshark.com', '8.8.8.8'],
                                              environment=environments)

            logger.info("...start vpn container successfully")
            self.vpn_container = container
        return self.vpn_container

    def load_vpn_container(self, *, client=None):
        if client is None:
            client = docker_client
        try:
            container = client.containers.get(self.vpn_container_name)
            logger.info(f"...find vpn container: {container.name}")
            if container.status != 'running':
                logger.info("[WARNING] container status is not running, restarting...")
                container.remove()
                raise Exception("container is not running")
        except docker.errors.NotFound:
            return None
        return container

    # create squid container
    def create_squid_container(self, *, client=None, detach=True):
        if client is None:
            client = docker_client

        if self.squid_container is None:
            logger.info("...starting squid container...")
            container = client.containers.run(image=self.squid_image, name=self.squid_container_name,
                                              detach=detach,
                                              volumes=[f'{self.base_dir}/squid/squid.conf:/etc/squid/squid.conf',
                                                       f'{self.base_dir}/squid/squid.passwd:/etc/squid/passwd',
                                                       f'{self.base_dir}/squid/:/var/spool/squid'],
                                              network_mode=f"container:{self.vpn_container.name}")
            logger.info(f"...start squid container successfully, expose port: {self.expose_port}")
            self.squid_container = container
        return self.squid_container

    def load_squid_container(self, *, client=None):
        if client is None:
            client = docker_client
        try:
            container = client.containers.get(self.squid_container_name)
            logger.info(f"...find squid container: {container.name}")
            if container.status != 'running':
                logger.info("[WARNING] container status is not running, restarting...")
                container.remove()
                # raise Exception("container is not running")

        except docker.errors.NotFound:
            return None
        return container

    def start_vpn_service(self):
        logger.info("...starting vpn container...")
        if self.vpn_container is None:
            self.vpn_container = self.create_vpn_container()
        elif self.vpn_container.status != 'running':
            self.vpn_container.start()
        logger.info("...start vpn container successfully")

    def start_squid_service(self):
        logger.info("...starting squid container...")
        if self.squid_container is None:
            self.squid_container = self.create_squid_container()
        elif self.squid_container.status != 'running':
            self.squid_container.start()
        logger.info("...start squid container successfully")

    def stop_vpn_service(self):
        logger.info("stopping vpn service...")
        if self.vpn_container:
            if self.vpn_container.status == 'running':
                self.vpn_container.stop()
            try:
                self.vpn_container.remove()
            except docker.errors.NotFound:
                pass
            except docker.errors.APIError:
                pass
        else:
            logger.info(f"vpn container {self.vpn_container_name} not found")

    def stop_squid_service(self):
        logger.info("stopping squid service...")
        if self.squid_container:
            if self.squid_container.status == 'running':
                self.squid_container.stop()
            try:
                self.squid_container.remove()
            except docker.errors.NotFound:
                pass
            except docker.errors.APIError:
                pass
        else:
            logger.info(f"squid container {self.squid_container_name} not found")

    def restart_vpn_service(self):
        logger.info("restarting vpn service...")
        if self.vpn_container:
            if self.vpn_container.status == 'running':
                self.vpn_container.restart()
        else:
            self.start_vpn_service()

    def restart_squid_service(self):
        logger.info("restarting squid service...")
        if self.squid_container:
            if self.squid_container.status == 'running':
                self.squid_container.restart()
        else:
            self.start_squid_service()

    def stop_service(self):
        logger.info("stopping service...")
        self.stop_squid_service()
        self.stop_vpn_service()
        return self.status

    def start_service(self):
        logger.info("...starting service...")
        self.start_vpn_service()
        self.start_squid_service()
        return self.status

    def restart_service(self):
        logger.info("restarting service...")
        self.restart_vpn_service()
        self.restart_squid_service()
        return self.status
