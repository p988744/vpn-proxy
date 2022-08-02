import click

from db.crud.proxies import create_service, stop_service, restart_service, get_proxy_units
from utils.utils import get_my_ip, get_my_country_code, get_local_ip


@click.group()
def cli():
    pass


@cli.command()
def list_proxy_unit():
    for unit in get_proxy_units():
        click.echo(unit.__str__())


@cli.command()
def host_info():
    host_ip = get_my_ip()
    host_country_code = get_my_country_code()
    local_ip = get_local_ip()
    click.echo(f"{host_ip=}, {host_country_code=}, {local_ip=}")


@cli.command()
@click.argument("config_name", default="all")
def start(config_name: str = 'all'):
    if config_name == 'all':
        config_name = None
    create_service([config_name])


@cli.command()
@click.argument("config_name", default="all")
def stop(config_name: str = 'all'):
    if config_name == 'all':
        config_name = None
    stop_service([config_name])


@cli.command()
@click.argument("config_name", default="all")
def restart(config_name: str = 'all'):
    if config_name == 'all':
        config_name = None
    restart_service([config_name])


if __name__ == '__main__':
    cli()
