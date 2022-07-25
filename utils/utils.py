import ipaddress
import socket
from typing import Iterable

import requests
import yaml
from yaml import Loader

from settings import settings
from utils.proxy_unit import ProxyUnit


def check_is_ip_format(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return ip_address
    except ValueError:
        return False


def get_ip(container):
    result = container.exec_run("curl -s https://ifconfig.io/forwarded")
    return result.output.decode('utf-8')


def get_country_code(container):
    result = container.exec_run("curl -s https://ifconfig.io/country_code")
    return result.output.decode('utf-8')


def get_my_ip(proxy=None):
    extra = {}
    if proxy:
        extra.update({'proxies': {'http': proxy, 'https': proxy}})
    try:
        ip = requests.get('https://ifconfig.io/forwarded', **extra).text.strip()
        return check_is_ip_format(ip)
    except:
        return None


def get_my_country_code(proxy=None):
    extra = {}
    if proxy:
        extra.update({'proxies': {'http': proxy, 'https': proxy}})
    try:
        return requests.get('https://ifconfig.io/country_code', **extra).text.strip()
    except:
        return None


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def stop_all_squid_unit(proxy_units: Iterable[ProxyUnit]):
    for squid_unit in proxy_units:
        squid_unit.stop_service()


def restart_all_squid_unit(proxy_units: Iterable[ProxyUnit]):
    for squid_unit in proxy_units:
        squid_unit.restart_service()
