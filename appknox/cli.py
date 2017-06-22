# (c) 2017, XYSec Labs

import base64
import click
import logging
import yaml

from appknox.client import AppknoxClient
from appknox.defaults import DEFAULT_API_HOST


@click.group()
@click.option('-v', '--verbose', count=True, help='Specify log verbosity.')
@click.pass_context
def cli(ctx, verbose):
    """
    Command line wrapper for the Appknox API
    """
    if verbose == 1:
        ctx.obj['LOG_LEVEL'] = logging.INFO
    elif verbose > 1:
        ctx.obj['LOG_LEVEL'] = logging.DEBUG
    else:
        ctx.obj['LOG_LEVEL'] = logging.WARNING


@cli.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--host', default=DEFAULT_API_HOST)
@click.pass_context
def login(ctx, username, password, host):
    """
    Log in to Appknox
    """
    client = AppknoxClient(
        username, password, host, log_level=ctx.obj['LOG_LEVEL'])
    client.login(persist=True)
    click.echo('Logged in to {}'.format(host))


@cli.command()
@click.pass_context
def whoami(ctx):
    """
    Show session info
    """
    client = AppknoxClient(persist=True, log_level=ctx.obj['LOG_LEVEL'])
    data = client.current_user()
    data['session'] = {'username': client.username,
                       'user_id': client.user_id,
                       'host': client.host,
                       'token': client.token}
    click.echo(yaml.dump(data))


@cli.command()
@click.pass_context
def project_list(ctx):
    """
    List projects
    """
    client = AppknoxClient(persist=True, log_level=ctx.obj['LOG_LEVEL'])
    data = client.project_list()
    click.echo(yaml.dump(data))


@cli.command()
@click.argument('package')
@click.pass_context
def upload(ctx):
    """
    Upload package
    """
    pass


@cli.command()
@click.argument('project_id')
def project_get(project_id):
    """
    Show project
    """
    client = AppknoxClient(persist=True, log_level=ctx.obj['LOG_LEVEL'])


@cli.command()
@click.argument('project_id')
def file_list(project_id):
    """
    List files for project
    """
    client = AppknoxClient(persist=True, log_level=ctx.obj['LOG_LEVEL'])


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


def main():
    cli(obj=dict())
