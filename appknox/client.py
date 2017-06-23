# (c) 2017, XYSec Labs

import logging
import requests
import slumber

from urllib.parse import urljoin

from appknox.exceptions import OneTimePasswordError, CredentialError, \
    ResponseError
from appknox.defaults import DEFAULT_VULNERABILITY_LANGUAGE, \
    DEFAULT_API_HOST, DEFAULT_REPORT_LANGUAGE, DEFAULT_REPORT_FORMAT
from appknox.mapper import mapper, Analysis, File, Project, User


class AppknoxClient(object):
    def __init__(self, username=None, password=None, user_id=None, token=None,
                 host=DEFAULT_API_HOST, log_level=logging.INFO):
        """
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        :param user_id:
        :type user_id: int
        :param token:
        :type token: str
        :param host: API host
        :type host: str
        """
        logging.basicConfig(level=log_level)

        self.host = host
        self.username = username
        self.password = password
        self.user_id = user_id
        self.token = token
        self.endpoint = urljoin(self.host, 'api/')

        self.api = slumber.API(self.endpoint, auth=(self.user_id, self.token),
                               append_slash=False)

    def login(self, otp=None):
        """
        :param otp: One-time password, if account has MFA enabled
        :type otp: int
        """

        if not self.username or not self.password:
            raise CredentialError('Both username and password are required')

        data = {
            'username': self.username,
            'password': self.password,
        }

        if otp:
            data['otp'] = str(otp)

        response = requests.post(urljoin(self.host, 'api/login/'), data=data)

        if response.status_code == 401:
            raise OneTimePasswordError(response.json()['message'])
        elif response.status_code == 403:
            raise CredentialError(response.json()['message'])

        json = response.json()
        self.token = json['token']
        self.user_id = str(json['user_id'])

    def get_user(self, user_id):
        user = self.api.users(user_id).get()

        return mapper(User, user)

    def get_project(self, project_id):
        project = self.api.projects(project_id).get()

        return mapper(Project, project)

    def list_projects(self):
        projects = self.api.projects().get(limit=-1)

        return [mapper(Project, dict(data=_)) for _ in projects['data']]

    def get_file(self, file_id):
        file_ = self.api.files(file_id).get()

        return mapper(File, file_)

    def list_files(self, project_id):
        files = self.api.files().get(projectId=project_id, limit=-1)
        
        return [mapper(File, dict(data=_)) for _ in files['data']]

    def upload_file(self, file_):
        data = {'content_type': 'application/octet-stream'}
        response = self.api.signed_url.get(data)

        url = response['url']
        data=file_.read()
        response = requests.put(url, data=data)

        url = 'uploaded_file'
        data = {
            'file_key': json['file_key'],
            'file_key_signed': json['file_key_signed']}
        response = self._request(requests.post, url, data=data, auth=(self.user_id, self.token))

        return response


    def start_dynamic(self, file_id):
        pass

    def stop_dynamic(self, file_id):
        pass

    def list_analyses(self, file_id):
        pass

    def get_report(self, file_id):
        pass
