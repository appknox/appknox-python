#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: __init__.py
Version: 0.1
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2015-08-07
"""
__author__ = "dhilipsiva"
__status__ = "development"

"""
Python wrapper for Appknox's REST API
"""

import requests
from appknox.errors import MissingCredentialsError, InvalidCredentialsError


class AppknoxClient(object):
    """
    Appknox Client
    """

    def login(self):
        """
        Login and Get token
        """
        login_url = "%s/token/new.json" % self.api_base
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = requests.post(login_url, data=data)
        json = response.json()
        if not json['success']:
            raise InvalidCredentialsError
        self.token = json['token']
        self.user_id = json['user']

    def __init__(
            self, username=None, password=None, api_key=None,
            instance_domain="beta.appknox.com", secure=True, auto_login=True):
        super(AppknoxClient, self).__init__()
        if username and password:
            self.basic_auth = True
            self.username = username
            self.password = password
        # API auth comes later
        # elif api_key:
        #     self.basic_auth = False
        #     self.api_key = api_key
        else:
            raise MissingCredentialsError
        protocol = 'http'
        if secure:
            protocol += 's'
        self.api_base = "%s://%s/api" % (protocol, instance_domain)
        if auto_login:
            self.login()
