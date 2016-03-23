#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: appknox.py
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2016-03-22
"""

import logging

import requests

from appknox.errors import MissingCredentialsError, InvalidCredentialsError, \
    ResponseError, InvalidReportTypeError

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
            'username': self._username,
            'password': self._password,
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
            host="beta.appknox.com", secure=True, auto_login=True):
        if username and password:
            self.basic_auth = True
            self._username = username
            self._password = password
        # API auth comes later
        # elif api_key:
        #     self.basic_auth = False
        #     self.api_key = api_key
        else:
            raise MissingCredentialsError
        protocol = 'http'
        if secure:
            protocol += 's'
        self.api_base = "%s://%s/api" % (protocol, host)
        self.login()

    def _request(self, req, endpoint, data={}, is_json=True):
        """
        Make a request
        """
        url = "%s/%s" % (self.api_base, endpoint)
        logger.debug('Making a request: %s', url)
        response = req(url, data=data, auth=(self.user_id, self.token))
        if response.status_code > 299 or response.status_code < 200:
            # f = open("error.html", "w")
            # f.write(response.content.decode())
            # f.close()
            raise ResponseError(response.content)
        if not is_json:
            return response.content
        json = response.json()
        return json

    def submit_url(self, store_url):
        """
        Submit a play store URL
        """
        data = {"storeURL": store_url}
        return self._request(requests.post, 'store_url', data)

    def upload_file(self, _file):
        """
        `_file` is a file-type object
        """
        data = {'content_type': 'application/octet-stream'}
        json = self._request(requests.get, 'signed_url', data)
        url = json['url']
        logger.info('Please wait while uploading file..: %s', url)
        response = requests.put(url, data=_file.read())
        # print(response.content, response.status_code)
        data = {
            "file_key": json['file_key'],
            "file_key_signed": json['file_key_signed'],
        }
        url = "%s/uploaded_file" % self.api_base
        response = requests.post(
            url, data=data, auth=(self.user_id, self.token))
        return response.json()

    def project_list(self):
        """
        return list of projects
        """
        return self._request(requests.get, 'projects')

    def project_get(self, project_id):
        """
        get project details with project id
        """
        url = 'projects/' + str(project_id)
        return self._request(requests.get, url)

    def file_list(self, project_id):
        """
        return list of files for a project
        """
        url = 'projects/' + str(project_id) + '/files'
        return self._request(requests.get, url)

    def file_get(self, file_id):
        """
        get file details with file id
        """
        url = 'files/' + str(file_id)
        return self._request(requests.get, url)

    def analyses_list(self, file_id):
        """
        get analyses details with file id
        """
        url = 'files/' + str(file_id) + '/analyses'
        return self._request(requests.get, url)

    def report(self, file_id, format_type):
        """
        get report in specified format
        """
        if format_type not in ['pdf', 'xml', 'csv', 'json']:
            raise InvalidReportTypeError("Invalid format type")
        url = 'report/' + str(file_id) + '?format=' + format_type
        return self._request(requests.get, url, is_json=False)
