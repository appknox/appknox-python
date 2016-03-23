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
__author__ = "dhilipsiva"
__status__ = "development"

"""
CLI program
"""

APPKNOX = """
.______  ._______ ._______ .____/\ .______  ._______   ____   ____
:      \ : ____  |: ____  |:   /  \:      \ : .___  \  \   \_/   /
|   .   ||    :  ||    :  ||.  ___/|       || :   |  |  \___ ___/
|   :   ||   |___||   |___||     \ |   |   ||     :  |  /   _   \\
|___|   ||___|    |___|    |      \|___|   | \______/  /___/ \___\\
    |___|                  |___\  /    |___|
                                \/
"""


import logging

from click import option, echo, group, make_pass_decorator, argument, File

from appknox import AppknoxClient
from pprint import pprint
logger = logging.getLogger("appknox")
logger.setLevel(10)


class Config(object):
    def __init__(self):
        self.client = None

pass_config = make_pass_decorator(Config, ensure=True)


@group()
@option('--username', envvar='APPKNOX_USERNAME', help="Username")
@option('--password', envvar='APPKNOX_PASSWORD', help="Password")
@option('--level', default=10, help="Log Level")
@option('--host', default='beta.appknox.com', help="Set Host")
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
@pass_config
def project_list(config):
    """
    Get a list of your projects
    """
    echo("Get list of your projects")
    pprint(config.client.project_list())


@cli.command()
@argument('project_id')
@pass_config
def project_get(config, project_id):
    """
    Get a particular project with id
    """
    echo("Get a particular project with id")
    pprint(config.client.project_get(project_id))


"""
@cli.command()
@argument('project_id')
@pass_config
def project_delete(config, project_id):
    echo("Delete a particular project with id")
    pprint(config.client.project_delete(project_id))
"""


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
def file_get(config, file_id):
    """
    Get a file with id
    """
    echo("Get a file with id")
    pprint(config.client.file_get(file_id))


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
@pass_config
def report(config, file_id, format_type):
    """
    Get report with format_type and file_id
    """
    echo("Get file report by specifying format and file id")
    response = config.client.report(file_id, format_type)
    return pprint(response.decode())
