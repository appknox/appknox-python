# (c) 2017, XYSec Labs

import click
import configparser
import logging
import os
import requests
import sys
import tabulate

from click import echo

from appknox.client import Appknox, DEFAULT_API_HOST
from appknox.exceptions import AppknoxError, OneTimePasswordError, \
    CredentialError, ReportError
from appknox.mapper import Analysis, File, Project, User, Vulnerability

DEFAULT_SESSION_PATH = '~/.config/appknox.ini'


def table(model, instances, ignore=list()):
    """
    Helper for tabulating data

    :param model: Model defined in `appknox.mapper`
    :param instances: Instance(s) to be tabulated
    :param ignore: Fields to be hidden in table
    """
    columns = list()
    for field in model._fields:
        if field not in ignore:
            columns.append(field)

    rows = list()

    if type(instances) is not list:
        instances = [instances]

    for instance in instances:
        row = [instance.__getattribute__(_) for _ in columns]
        rows.append(row)

    return tabulate.tabulate(rows, headers=columns)


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

        ctx.obj['CLIENT'] = Appknox(
            username=username, user_id=user_id, token=token, host=host,
            log_level=ctx.obj['LOG_LEVEL'])
    else:
        if ctx.invoked_subcommand not in ['login', 'logout']:
            echo('Not logged in')
            sys.exit(1)


@cli.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--host', default=DEFAULT_API_HOST)
@click.pass_context
def login(ctx, username, password, host):
    """
    Log in and save session credentials
    """
    ctx.obj['CLIENT'] = client = Appknox(
        username=username, password=password, host=host,
        log_level=ctx.obj['LOG_LEVEL'])
    try:
        client.login()
    except requests.exceptions.InvalidSchema as e:
        echo(e)
        echo('Perhaps you missed http/https in host?')
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        echo(e)
        echo('Perhaps your network is down?')
        sys.exit(1)
    except OneTimePasswordError as e:
        otp = click.prompt('OTP', type=int)
        try:
            client.login(otp=otp)
        except CredentialError as e:
            echo(e)
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
    data = client.get_user(client.user_id)
    echo(table(User, data))


@cli.command()
@click.pass_context
def logout(ctx):
    """
    Delete session credentials
    """
    try:
        os.remove(os.path.expanduser(DEFAULT_SESSION_PATH))
    except FileNotFoundError:
        echo('Not logged in')
        sys.exit(1)


@cli.command()
@click.pass_context
def projects(ctx):
    """
    List projects
    """
    client = ctx.obj['CLIENT']
    echo(table(Project, client.get_projects()))


@cli.command()
@click.argument('project_id')
@click.pass_context
def files(ctx, project_id):
    """
    List files for project
    """
    client = ctx.obj['CLIENT']
    echo(table(File, client.get_files(project_id)))


@cli.command()
@click.argument('path')
@click.pass_context
def upload(ctx, path):
    """
    Upload and scan package
    """
    client = ctx.obj['CLIENT']
    try:
        file_ = open(path, 'rb')
    except FileNotFoundError as e:
        echo(e)
        sys.exit(1)
    client.upload_file(file_)


@cli.command()
@click.argument('file_id')
@click.pass_context
def analyses(ctx, file_id):
    """
    List analyses for file
    """
    client = ctx.obj['CLIENT']
    echo(table(Analysis, client.get_analyses(file_id), ignore=['findings']))


@cli.command()
@click.argument('vulnerability_id')
@click.pass_context
def vulnerability(ctx, vulnerability_id):
    """
    Get vulnerability
    """
    client = ctx.obj['CLIENT']
    echo(table(Vulnerability, client.get_vulnerability(vulnerability_id)))


@cli.command()
@click.argument('file_id')
@click.option(
    '-f', '--format', default='json', help='Report format: json, pdf')
@click.option(
    '-l', '--language', default='en', help='Report language: en, ja')
@click.pass_context
def report(ctx, file_id, format, language):
    """
    Download report for file
    """
    client = ctx.obj['CLIENT']
    try:
        echo(client.get_report(file_id, format=format, language=language))
    except ReportError as e:
        echo(e)
        sys.exit(1)


@cli.command()
@click.argument('file_id')
@click.pass_context
def dynamic_start(ctx, file_id):
    """
    Start dynamic scan for file
    """
    client = ctx.obj['CLIENT']
    client.start_dynamic(file_id)


@cli.command()
@click.argument('file_id')
@click.pass_context
def dynamic_stop(ctx, file_id):
    """
    Stop dynamic scan for file
    """
    client = ctx.obj['CLIENT']
    client.stop_dynamic(file_id)


def main():
    cli(obj=dict())
