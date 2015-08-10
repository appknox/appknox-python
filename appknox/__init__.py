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

import logging

import requests

from appknox.errors import MissingCredentialsError, InvalidCredentialsError, \
    ResponseError

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("appknox")


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
        logger.debug('Logging In: %s', login_url)
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
        self.login()

    def _make_request(self, req, endpoint, data):
        """
        Make Arequest
        """
        url = "%s/%s" % (self.api_base, endpoint)
        response = req(
            url, data=data, auth=(self.user_id, self.token))
        json = response.json()
        if response.status_code > 299 or response.status_code < 200:
            raise ResponseError(json.get("message"))
        logger.debug('Making a request: %s', url)
        return json

    def submit_url(self, store_url):
        """
        Submit a play store URL
        """
        data = {"storeURL": store_url}
        return self._make_request(requests.post, 'store_url', data)
