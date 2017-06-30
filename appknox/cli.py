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

CONFIG_FILE = os.path.expanduser('~/.config/appknox.ini')
DEFAULT_PROFILE = 'default'

config = configparser.ConfigParser()
config.read(CONFIG_FILE)


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


def get_profile(name):
    try:
        profile = config[name]
    except KeyError:
        profile = None
    return profile


def save_profile(name, data):
    config[name] = data
    with open(CONFIG_FILE, 'w') as fh:
        config.write(fh)


def remove_profile(name):
    result = config.remove_section(name)
    with open(CONFIG_FILE, 'w') as fh:
        config.write(fh)
    return result


@click.group()
@click.option('-v', '--verbose', count=True, help='Specify log verbosity.')
@click.option('-n', '--profile', default=DEFAULT_PROFILE)
@click.pass_context
def cli(ctx, verbose, profile):
    """
    Command line wrapper for the Appknox API
    """
    if verbose == 1:
        ctx.obj['LOG_LEVEL'] = logging.INFO
    elif verbose > 1:
        ctx.obj['LOG_LEVEL'] = logging.DEBUG
    else:
        ctx.obj['LOG_LEVEL'] = logging.WARNING

    ctx.obj['PROFILE'] = profile

    logging.basicConfig(level=ctx.obj['LOG_LEVEL'])
    profile = get_profile(profile)
    if profile:
        ctx.obj['CLIENT'] = Appknox(
            username=profile['username'], user_id=profile['user_id'],
            token=profile['token'], host=profile['host'],
        )
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

    data = {
        'username': username,
        'user_id': client.user_id,
        'token': client.token,
        'host': host,
    }
    save_profile(name=ctx.obj['PROFILE'], data=data)
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
    profile = ctx.obj['PROFILE']
    success = remove_profile(profile)
    if success:
        echo('Logged out')
    else:
        echo('Not logged in')


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
