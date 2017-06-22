# (c) 2017, XYSec Labs

import base64
import click
import logging

from tabulate import tabulate

from appknox.client import AppknoxClient
from appknox.constants import DEFAULT_API_HOST

logger = logging.getLogger('appknox')


@click.group()
@click.option('-v', '--verbose', count=True, help='Specify log verbosity.')
def cli(verbose):
    """
    Command line wrapper for the Appknox API
    """
    if verbose == 1:
        logger.setLevel(20)
    elif verbose >= 2:
        logger.setLevel(10)
    else:
        logger.setLevel(30)


@cli.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--host', default=DEFAULT_API_HOST)
def login(username, password, host):
    """
    Log in to Appknox
    """
    client = AppknoxClient(username, password, host)
    client.login(persist=True)
    click.echo('Logged in to {}'.format(host))


@cli.command()
def whoami():
    """
    Show session info
    """
    client = AppknoxClient(persist=True)
    click.echo(tabulate([
        ['username', client.username],
        ['user_id', client.user_id],
        ['host', client.host],
        ['token', client.token]
    ]))


@cli.command()
@click.argument('package')
def upload():
    """
    Upload package
    """
    client = AppknoxClient(persist=True)
    pass


@cli.command()
def project_list():
    """
    List projects
    """
    client = AppknoxClient(persist=True)
    client.project_list()
    pass


@cli.command()
@click.argument('project_id')
def project_get(project_id):
    """
    Show project
    """
    client = AppknoxClient(persist=True)
    pass


@cli.command()
@click.argument('project_id')
def file_list(project_id):
    """
    List files for project
    """
    client = AppknoxClient(persist=True)
    pass


@cli.command()
@click.argument('file_id')
def file_get(file_id):
    """
    Show file
    """
    client = AppknoxClient(persist=True)
    pass


@cli.command()
@click.argument('file_id')
def analyses_list(file_id):
    """
    List analyses for file
    """
    client = AppknoxClient(persist=True)
    pass


@cli.command()
@click.argument('file_id')
def dynamic_start(file_id):
    """
    Start dynamic scan for file
    """
    client = AppknoxClient(persist=True)
    pass


@cli.command()
@click.argument('file_id')
def dynamic_stop(file_id):
    """
    Stop dynamic scan for file
    """
    client = AppknoxClient(persist=True)
    pass
