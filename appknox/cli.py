# (c) 2017, XYSec Labs


import configparser
import logging
import os
import requests
import sys
import tabulate
import time

import click
from click import echo, echo_via_pager

from appknox.client import Appknox, DEFAULT_API_HOST
from appknox.exceptions import (
    AppknoxError, OneTimePasswordError, CredentialError,
    OrganizationError, UploadError
)
from appknox.mapper import (
    Analysis, File, Organization, Project, Vulnerability, OWASP,
    Submission, Whoami
)

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

    ctx.obj['USING_ENV_TOKEN'] = False

    logging.basicConfig(level=ctx.obj['LOG_LEVEL'])

    if (
        os.environ.get('APPKNOX_ACCESS_TOKEN') and
        ctx.invoked_subcommand in ['login', 'logout']
    ):
        logging.error(
            'this command is not supported when using access token in '
            'environment variables'
        )
        sys.exit(1)

    if ctx.invoked_subcommand in ['login']:
        return

    profile = get_profile(profile)

    if os.environ.get('APPKNOX_ACCESS_TOKEN'):
        profile = dict()
        profile['access_token'] = os.environ.get('APPKNOX_ACCESS_TOKEN')
        profile['host'] = os.environ.get('APPKNOX_HOST')
        profile['organization_id'] = os.environ.get('APPKNOX_ORGANIZATION_ID')
        ctx.obj['USING_ENV_TOKEN'] = True

    if not profile:
        echo('Not logged in')
        sys.exit(1)

    if not profile.get('access_token', None):
        echo('Access token doesn\'t exist. Login again')
        sys.exit(1)

    ctx.obj['CLIENT'] = Appknox(
        username=profile.get('username'), host=profile.get('host'),
        token=profile.get('token'), access_token=profile.get('access_token'),
        user_id=profile.get('user_id'),
        organization_id=profile.get('organization_id')
    )


@cli.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--host', envvar='APPKNOX_HOST', default=DEFAULT_API_HOST)
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
    except OneTimePasswordError:
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
        'organization_id': client.organization_id,
        'token': client.token,
        'access_token': client.access_token,
        'host': host,
        'timestamp': str(int(time.time())),
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
    data = client.get_whoami()
    echo(table(Whoami, data))


@cli.command()
@click.pass_context
def logout(ctx):
    """
    Delete session credentials
    """
    profile = ctx.obj['PROFILE']
    success = remove_profile(profile)

    client = ctx.obj['CLIENT']
    client.revoke_access_token()

    if success:
        echo('Logged out')
    else:
        echo('Not logged in')


@cli.command()
@click.pass_context
def organizations(ctx):
    """
    List organizations
    """
    client = ctx.obj['CLIENT']
    echo_via_pager(table(Organization, client.get_organizations()))


@cli.command()
@click.option('--platform', type=int, help='Project Platform')
@click.option('--package_name', default='', type=str, help='Package Name')
@click.option('-q', '--query', default='', type=str, help='Search Query')
@click.pass_context
def projects(ctx, platform, package_name, query):
    """
    List projects
    """
    client = ctx.obj['CLIENT']
    echo_via_pager(table(
        Project, client.get_projects(platform, package_name, query)
    ))


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
@click.argument('path', type=click.Path(exists=True))
@click.pass_context
def upload(ctx, path):
    """
    Upload and scan package
    """
    client = ctx.obj['CLIENT']
    try:
        file_ = open(path, 'rb')
        file_data = file_.read()
    except FileNotFoundError as e:
        echo(e)
        sys.exit(1)
    try:
        file_id = client.upload_file(file_data)
        echo("Upload Successful, file_id: {}".format(file_id))
    except UploadError as e:
        echo(e)
        sys.exit(1)


@cli.command()
@click.argument('file_id')
@click.pass_context
def analyses(ctx, file_id):
    """
    List analyses for file
    """
    client = ctx.obj['CLIENT']
    echo(table(
        Analysis, client.get_analyses(file_id),
        ignore=[
            'cvss_vector', 'cvss_version', 'cvss_metrics_humanized', 'findings'
        ]
    ))


@cli.command('recent_uploads')
@click.pass_context
def recent_uploads(ctx):
    """
    List recent file uploads by the user
    """
    client = ctx.obj['CLIENT']
    echo(table(
        Submission, client.recent_uploads()
    ))


@cli.command()
@click.argument('vulnerability_id')
@click.pass_context
def vulnerability(ctx, vulnerability_id):
    """
    Get vulnerability
    """
    client = ctx.obj['CLIENT']
    echo(table(
        Vulnerability, client.get_vulnerability(vulnerability_id),
        ignore=[
            'related_to', 'business_implication', 'types'
        ]
    ))


@cli.command()
@click.argument('owasp_id')
@click.pass_context
def owasp(ctx, owasp_id):
    """
    Get owasp
    """
    client = ctx.obj['CLIENT']
    echo(table(OWASP, client.get_owasp(owasp_id), ignore=['description']))


# @cli.command()
# @click.argument('file_id')
# @click.option(
#     '-f', '--format', default='json', help='Report format: json, pdf')
# @click.option(
#     '-l', '--language', default='en', help='Report language: en, ja')
# @click.pass_context
# def report(ctx, file_id, format, language):
#     """
#     Download report for file
#     """
#     client = ctx.obj['CLIENT']
#     try:
#         echo(client.get_report(file_id, format=format, language=language))
#     except ReportError as e:
#         echo(e)
#         sys.exit(1)


@cli.command('switch_organization')
@click.argument('organization_id')
@click.pass_context
def switch_organization(ctx, organization_id):
    """
    Switch organization in client instance
    """

    if ctx.obj['USING_ENV_TOKEN']:
        logging.error(
            'switch_organization is not supported when using access token in '
            'environment variables'
        )
        sys.exit(1)
    client = ctx.obj['CLIENT']
    is_switched = client.switch_organization(organization_id)

    if not is_switched:
        echo(OrganizationError('Not found!'))
        sys.exit(1)

    profile_name = ctx.obj['PROFILE']
    profile = get_profile(profile_name)
    data = {item[0]: item[1] for item in profile.items()}
    if organization_id == data['organization_id']:
        return

    data['organization_id'] = organization_id
    save_profile(name=profile_name, data=data)
    echo('Switched organization to {}'.format(organization_id))


def main():
    cli(obj=dict())
