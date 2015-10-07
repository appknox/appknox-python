#

"""
File name: appknox.py
Version: 0.1
Author: rmad17 <sourav@appknox.com>
Date created: 2015-10-06
"""
__author__ = "rmad17"
__status__ = "development"

"""
Python wrapper for Appknox's REST API
"""

import logging

import requests

from errors import MissingCredentialsError, InvalidCredentialsError, \
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
            host="beta.appknox.com", secure=True, auto_login=True):
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
        self.api_base = "%s://%s/api" % (protocol, host)
        self.login()

    def _request(self, req, endpoint, data={}):
        """
        Make a request
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
        return self._request(requests.post, 'store_url', data)

    def upload_file(self, _file):
        """
        `_file` is a file-type object
        """
        data = {'content_type': 'application/octet-stream'}
        json = self._request(requests.get, 'signed_url', data)
        url = json['base_url']
        logger.info('Please wait while uploading file..: %s', url)
        requests.put(url, data=_file.read())
        data = {
            "file_key": json['file_key'],
            "file_key_signed": json['file_key_signed'],
        }
        return self._request(requests.post, 'uploaded_file', data)

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

    def project_delete(self, project_id):
        """
        delete project with project id
        """
        url = 'projects/delete/' + str(project_id)
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
