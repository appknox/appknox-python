import base64
import logging

from click import option, echo, group, make_pass_decorator, argument, File

from appknox import AppknoxClient, DEFAULT_VULNERABILITY_LANGUAGE, \
    DEFAULT_APPKNOX_URL, DEFAULT_LIMIT, DEFAULT_REPORT_LANGUAGE, \
    DEFAULT_OFFSET, DEFAULT_REPORT_FORMAT, DEFAULT_LOG_LEVEL
from pprint import pprint

logger = logging.getLogger("appknox")
logger.setLevel(10)


__author__ = "dhilipsiva"
__status__ = "development"


APPKNOX = """
.______  ._______ ._______ .____/\ .______  ._______   ____   ____
:      \ : ____  |: ____  |:   /  \:      \ : .___  \  \   \_/   /
|   .   ||    :  ||    :  ||.  ___/|       || :   |  |  \___ ___/
|   :   ||   |___||   |___||     \ |   |   ||     :  |  /   _   \\
|___|   ||___|    |___|    |      \|___|   | \______/  /___/ \___\\
    |___|                  |___\  /    |___|
                                \/
"""


class Config(object):
    def __init__(self):
        self.client = None


pass_config = make_pass_decorator(Config, ensure=True)


@group()
@option('--username', envvar='APPKNOX_USERNAME', help="Username")
@option('--password', envvar='APPKNOX_PASSWORD', help="Password")
@option('--level', default=DEFAULT_LOG_LEVEL, help="Log level")
@option('--host', default=DEFAULT_APPKNOX_URL, help="API host")
@pass_config
def cli(config, username, password, level, host):
    """
    Command line wrapper for the Appknox API
    """
    echo(APPKNOX)
    logger.setLevel(level)
    config.client = AppknoxClient(
        username=username, password=password, host=host)


@cli.command()
@pass_config
def validate(config):
    """
    Validate if credentials are correct
    """
    pprint(config.client.current_user())
    pprint(dict(user_id=config.client.user,
                token=config.client.token,
                base64_token=base64.b64encode('{}:{}'.format(
                    config.client.user, config.client.token).encode('ascii'))))
    echo("Credentials are valid")


@cli.command()
@argument('url')
@pass_config
def submit_url(config, url):
    """
    Submit app by store URL
    """
    echo("Submitting store URL")
    config.client.submit_url(url)


@cli.command()
@argument('file', type=File('rb'))
@pass_config
def upload(config, file):
    """
    Submit app by uploading file
    """
    config.client.upload_file(file)


@cli.command()
@argument('project_id')
@pass_config
def project_get(config, project_id):
    """
    Get project by ID
    """
    echo("Get project by ID")
    pprint(config.client.project_get(project_id))


@cli.command()
@option(
    '--limit', default=DEFAULT_LIMIT, help="Limit of projects to retrieve")
@option(
    '--offset', default=DEFAULT_OFFSET, help="Project offset")
@pass_config
def project_list(config, limit, offset):
    """
    Get list of projects
    """
    echo("Get list of projects")
    pprint(config.client.project_list(limit, offset))


@cli.command()
@argument('file_id')
@pass_config
def file_get(config, file_id):
    """
    Get file by ID
    """
    echo("Get file by ID")
    pprint(config.client.file_get(file_id))


@cli.command()
@option(
    '--limit', default=DEFAULT_LIMIT, help="Limit of files to retrieve")
@option(
    '--offset', default=DEFAULT_OFFSET, help="File offset")
@argument('project_id')
@pass_config
def file_list(config, project_id, limit, offset):
    """
    Get list of files for a project with ID
    """
    echo("Get list of files for a project with ID")
    pprint(config.client.file_list(project_id, limit, offset))


@cli.command()
@argument('file_id')
@pass_config
def dynamic_start(config, file_id):
    """
    Start dynamic scan for file
    """
    echo("Starting dynamic scan for file {}".format(file_id))
    pprint(config.client.dynamic_start(file_id))


@cli.command()
@argument('file_id')
@pass_config
def dynamic_stop(config, file_id):
    """
    Stop dynamic scan for file
    """
    echo("Stopping dynamic scan for file {}".format(file_id))
    pprint(config.client.dynamic_stop(file_id))


@cli.command()
@argument('file_id')
@pass_config
def dynamic_restart(config, file_id):
    """
    Restart dynamic scan for file
    """
    echo("Restarting dynamic scan for file {}".format(file_id))
    pprint(config.client.dynamic_restart(file_id))


@cli.command()
@argument('file_id')
@pass_config
def analyses_list(config, file_id):
    """
    Get analyses by file ID
    """
    echo("Get analyses by file ID")
    pprint(config.client.analyses_list(file_id))


@cli.command()
@argument('file_id')
@option(
    '--format_type', default=DEFAULT_REPORT_FORMAT,
    help='Valid formats are json/pdf')
@option(
    '--language', default=DEFAULT_REPORT_LANGUAGE,
    help='Supported languages are en/ja')
@pass_config
def report(config, file_id, format_type, language):
    """
    Get report with format_type and file_id
    """
    echo("Get file report by specifying format and file ID")
    response = config.client.report(file_id, format_type, language)
    return pprint(response)


@cli.command()
@argument('card')
@pass_config
def payment(config, card):
    """
    Make payment
    """
    echo("Make a payment for user")
    response = config.client.payment(card)
    return pprint(response.decode())


@cli.command()
@argument('vulnerability_id')
@option(
    '--language', default=DEFAULT_VULNERABILITY_LANGUAGE,
    help='Supported languages are en/ja')
@pass_config
def vulnerability(config, vulnerability_id, language):
    """
    Get report with format_type and file_id
    """
    echo("Get file report by specifying format and file ID")
    response = config.client.vulnerability(vulnerability_id, language)
    return pprint(response)
