#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: cli.py
Version: 0.1
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2015-08-10
"""
import logging

from click import option, echo, group, make_pass_decorator, argument, File

from appknox import AppknoxClient, DEFAULT_APPKNOX_URL
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
@option('--level', default=10, help="Log Level")
@option('--host', default=DEFAULT_APPKNOX_URL, help="Set Host")
@option('--secure/--no-secure', default=True)
@pass_config
def cli(config, username, password, level, host, secure):
    """
    Command line tool For Appknox's REST API
    """
    echo(APPKNOX)
    logger.setLevel(level)
    config.client = AppknoxClient(
        username=username, password=password, host=host, secure=secure)


@cli.command()
@pass_config
def validate(config):
    """
    Validate if credentials are correct!
    """
    pprint(config.client.current_user())
    echo("Your credentials are valid!")


@cli.command()
@argument('url')
@pass_config
def submit_url(config, url):
    """
    Submit store urls!
    """
    echo("Submitting Store URL")
    config.client.submit_url(url)


@cli.command()
@argument('file', type=File('rb'))
@pass_config
def upload(config, file):
    """
    Upload a file!
    """
    config.client.upload_file(file)


@cli.command()
@argument('project_id')
@pass_config
def project_get(config, project_id):
    """
    Get a particular project with id
    """
    echo("Get a particular project with id")
    pprint(config.client.project_get(project_id))


@cli.command()
@pass_config
def project_list(config):
    """
    Get a list of your projects
    """
    echo("Get list of your projects")
    pprint(config.client.project_list())


@cli.command()
@argument('file_id')
@pass_config
def file_get(config, file_id):
    """
    Get a file with id
    """
    echo("Get a file with id")
    pprint(config.client.file_get(file_id))


@cli.command()
@argument('project_id')
@pass_config
def file_list(config, project_id):
    """
    Get list of files for a project with id
    """
    echo("Get list of files for a project with id")
    pprint(config.client.file_list(project_id))


@cli.command()
@argument('file_id')
@pass_config
def dynamic_start(config, file_id):
    """
    Start dynamic scan on the file
    """
    echo("Starting dynamic scan for file {}".format(file_id))
    pprint(config.client.dynamic_start(file_id))


@cli.command()
@argument('file_id')
@pass_config
def dynamic_stop(config, file_id):
    """
    Stop dynamic scan on the file
    """
    echo("Stopping dynamic scan for file {}".format(file_id))
    pprint(config.client.dynamic_stop(file_id))


@cli.command()
@argument('file_id')
@pass_config
def dynamic_restart(config, file_id):
    """
    Restart dynamic scan on the file
    """
    echo("Restarting dynamic scan for file {}".format(file_id))
    pprint(config.client.dynamic_restart(file_id))


@cli.command()
@argument('file_id')
@pass_config
def analyses_list(config, file_id):
    """
    Get analyses for a file with id
    """
    echo("Get analyses for a file with id")
    pprint(config.client.analyses_list(file_id))


@cli.command()
@argument('file_id')
@option('--format_type', default='json', help='Valid formats are \
        "pdf", "csv", "xml", "json"')
@option('--language', default='en',
        help='Supported languages are "en", "ja"')
@pass_config
def report(config, file_id, format_type, language):
    """
    Get report with format_type and file_id
    """
    echo("Get file report by specifying format and file id")
    response = config.client.report(file_id, format_type, language)
    return pprint(response.decode())


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
