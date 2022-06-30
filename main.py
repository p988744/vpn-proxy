from pathlib import Path

import requests

from squid_unit import SquidUnit

BASE_DIR = Path(__file__).parent
SURFSHARK_CONFIG = {
    "surfshark_user": "BMHeBFJg2EgJg9ECpPrreLah",
    "surfshark_password": "7sM2GJTHqsVVTWFCxJUGGrRj",
    "surfshark_country": 'us',
    "surfshark_city": 'nyc',
    "connection_type": "tcp",
}


def get_ip(container):
    result = container.exec_run("curl -s https://ifconfig.io/forwarded")
    return result.output.decode('utf-8')


def get_country_code(container):
    result = container.exec_run("curl -s https://ifconfig.io/country_code")
    return result.output.decode('utf-8')


if __name__ == '__main__':
    host_ip = requests.get("https://ifconfig.io/forwarded").content.decode('utf-8').strip()
    host_country_code = requests.get("https://ifconfig.io/country_code").content.decode('utf-8').strip()
    print(f"{host_ip=}, {host_country_code=}")
    unit = SquidUnit(**SURFSHARK_CONFIG)
    unit.start_service()

    while command := input("command: "):
        if command == "stop":
            unit.stop_service()
            break
        elif command == "start":
            unit.start_service()
        elif command == "restart":
            unit.restart_service()
        elif command == "status":
            print(unit.status())
        elif command == "ip":
            print(get_ip(unit.get_ip()))
        elif command == "country":
            print(get_country_code(unit.get_country_code()))
        elif command == "exit":
            break
        elif command == "help":
            print("""
            start: start service
            stop: stop service
            restart: restart service
            status: show service status
            ip: show ip
            country: show country code
            exit: exit
            help: show help
            """)
        else:
            print("unknown command")

    unit.stop_service()
