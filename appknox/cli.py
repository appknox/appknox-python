# (c) 2017, XYSec Labs

import click
import configparser
import logging
import os
import requests
import sys
import yaml

from click import echo
from tabulate import tabulate

from appknox.client import AppknoxClient
from appknox.defaults import DEFAULT_API_HOST, DEFAULT_SESSION_PATH
from appknox.exceptions import AppknoxError


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

    logging.basicConfig(level=ctx.obj['LOG_LEVEL'])

    config = configparser.ConfigParser()
    if config.read(os.path.expanduser(DEFAULT_SESSION_PATH)):
        user_id = config['DEFAULT']['user_id']
        username = config['DEFAULT']['username']
        token = config['DEFAULT']['token']
        host = config['DEFAULT']['host']

        ctx.obj['CLIENT'] = AppknoxClient(
            username=username, user_id=user_id, token=token, host=host,
            log_level=ctx.obj['LOG_LEVEL'])


@cli.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--host', default=DEFAULT_API_HOST)
@click.pass_context
def login(ctx, username, password, host):
    """
    Log in to Appknox
    """
    ctx.obj['CLIENT'] = client = AppknoxClient(
        username=username, password=password, host=host,
        log_level=ctx.obj['LOG_LEVEL'])
    try:
        client.login()
    except requests.exceptions.InvalidSchema as e:
        echo(e)
        echo('Perhaps you missed http/https?')
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        echo(e)
        echo('Perhaps your network is down?')
        sys.exit(1)
    except AppknoxError as e:
        echo(e)
        sys.exit(1)

    config = configparser.ConfigParser()
    config['DEFAULT']['username'] = username
    config['DEFAULT']['user_id'] = client.user_id
    config['DEFAULT']['token'] = client.token
    config['DEFAULT']['host'] = host

    if os.path.isfile(os.path.expanduser(DEFAULT_SESSION_PATH)):
        logging.warn('Overwriting existing local session')

    with open(os.path.expanduser(DEFAULT_SESSION_PATH), 'w') as f:
        config.write(f)
        logging.debug('Session credentials written to {}'.format(
            DEFAULT_SESSION_PATH))

    echo('Logged in to {}'.format(host))


@cli.command()
@click.pass_context
def whoami(ctx):
    """
    Show session info
    """
    client = ctx.obj['CLIENT']
    data = client.current_user()
    data['session'] = {'username': client.username,
                       'user_id': client.user_id,
                       'host': client.host,
                       'token': client.token}
    echo(yaml.dump(data))


@cli.command()
@click.pass_context
def logout(ctx):
    """
    Delete local session credentials
    """
    try:
        os.remove(os.path.expanduser(DEFAULT_SESSION_PATH))
    except FileNotFoundError:
        echo('Not logged in')
        sys.exit(1)


@cli.command()
@click.pass_context
def project_list(ctx):
    """
    List projects
    """
    client = ctx.obj['CLIENT']
    data = client.project_list()
    echo(yaml.dump(data))


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
    pass


@cli.command()
@click.argument('project_id')
def file_list(project_id):
    """
    List files for project
    """
    pass


@cli.command()
@click.argument('file_id')
def file_get(file_id):
    """
    Show file
    """
    pass


@cli.command()
@click.argument('file_id')
def analyses_list(file_id):
    """
    List analyses for file
    """
    pass


@cli.command()
@click.argument('file_id')
def dynamic_start(file_id):
    """
    Start dynamic scan for file
    """
    pass


@cli.command()
@click.argument('file_id')
def dynamic_stop(file_id):
    """
    Stop dynamic scan for file
    """
    pass


def main():
    cli(obj=dict())
