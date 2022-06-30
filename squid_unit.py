import time
from abc import ABC
from pathlib import Path

import docker


class SquidUnit(ABC):
    base_dir = Path(__file__).parent

    def __init__(self, surfshark_user, surfshark_password, surfshark_country='us', surfshark_city='nyc',
                 connection_type='tcp', expose_port=3128):
        self.surfshark_user = surfshark_user
        self.surfshark_password = surfshark_password
        self.surfshark_country = surfshark_country
        self.surfshark_city = surfshark_city
        self.connection_type = connection_type
        self.expose_port = expose_port
        self.client = docker.from_env()
        self.vpn_container = None
        self.squid_container = None

    @property
    def surfshark_config(self):
        return {
            "SURFSHARK_USER": self.surfshark_user,
            "SURFSHARK_PASSWORD": self.surfshark_password,
            "SURFSHARK_COUNTRY": self.surfshark_country,
            "SURFSHARK_CITY": self.surfshark_city,
            "CONNECTION_TYPE": self.connection_type,
        }

    # create docker container with name and volume
    def create_vpn_container(self, *, client=None, name=None, detach=True,
                             environments=None):
        if client is None:
            client = self.client
        if name is None:
            name = f"openvpn-client-{self.surfshark_country}-{self.surfshark_city}-{self.expose_port}"
        if environments is None:
            environments = self.surfshark_config
        try:
            container = self.client.containers.get(name)
            print("find exist vpn container")
        except docker.errors.NotFound:
            print("starting vpn container...")
            container = self.client.containers.run(image='ilteoood/docker-surfshark', name=name, cap_add=['NET_ADMIN'],
                                                   auto_remove=True,
                                                   ports={'3128/tcp': self.expose_port},
                                                   devices=['/dev/net/tun'], detach=detach,
                                                   dns=['surfshark.com', '8.8.8.8'],
                                                   environment=environments)

            print("...start vpn container successfully")

        return container

    # create squid container
    def create_squid_container(self, *, client=None, name=None, detach=True):
        if client is None:
            client = self.client
        if name is None:
            name = f"squid-{self.surfshark_country}-{self.surfshark_city}-{self.expose_port}"
        try:
            container = client.containers.get(name)
            print("find exist vpn container")
        except docker.errors.NotFound:
            print("starting squid container...")
            container = client.containers.run(image='sameersbn/squid:3.5.27-2', name=name, detach=detach,
                                              volumes=[f'{self.base_dir}/squid/squid.conf:/etc/squid/squid.conf',
                                                       f'{self.base_dir}/squid/squid.passwd:/etc/squid/passwd',
                                                       f'{self.base_dir}/squid/:/var/spool/squid'],
                                              network_mode=f"container:{self.vpn_container.name}")
            print("...start squid container successfully, expose port:", self.expose_port)
            print("...installing curl...")
            container.exec_run("apt update")
            container.exec_run("apt install -y curl")
            print("...installing curl...done")
        return container

    def start_service(self, retries=3, delay=5):
        if retries < 0:
            retries = 1
        i = 0
        for i in range(retries):
            try:
                self.vpn_container = self.create_vpn_container()
                self.squid_container = self.create_squid_container()
                print(self.status())
                break
            except Exception as e:
                print(e)
                if "port is already allocated" in e.explanation:
                    self.expose_port = self.expose_port + 1
                print(f"retry {i + 1}/{retries}")
                time.sleep(delay)
        if i == retries:
            raise Exception("failed to start service")

    def stop_service(self):
        self.vpn_container.stop()
        self.squid_container.stop()
        self.vpn_container.remove()
        self.squid_container.remove()

    def restart_service(self):
        self.vpn_container.restart()
        self.squid_container.restart()

    def status(self):
        return {
            "vpn_container_name": self.vpn_container.name,
            "vpn_container_status": self.vpn_container.status,
            "squid_container_name": self.squid_container.name,
            "squid_container_status": self.squid_container.status,
            "connection_type": self.connection_type,
            "ip": self.get_ip(),
            "country_code": self.get_country_code(),
        }

    def get_ip(self):
        result = self.squid_container.exec_run("curl -s https://ifconfig.io/forwarded")
        return result.output.decode('utf-8').strip()

    def get_country_code(self):
        result = self.squid_container.exec_run("curl -s https://ifconfig.io/country_code")
        return result.output.decode('utf-8').strip()
