# (c) 2017, XYSec Labs

import logging
import requests
import slumber

from urllib.parse import urljoin

from appknox.exceptions import OneTimePasswordError, CredentialError, \
    AppknoxError
from appknox.defaults import DEFAULT_VULNERABILITY_LANGUAGE, \
    DEFAULT_API_HOST, DEFAULT_REPORT_LANGUAGE, DEFAULT_REPORT_FORMAT
from appknox.mapper import mapper, Analysis, File, Project, User, Vulnerability


class AppknoxClient(object):
    """

    """

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
        Authenticate client with server

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

        response = requests.post(urljoin(self.host, 'api/login'), data=data)

        if response.status_code == 401:
            raise OneTimePasswordError(response.json()['message'])
        elif response.status_code == 403:
            raise CredentialError(response.json()['message'])
        elif response.status_code != 200:
            raise AppknoxError('Unknown error')

        json = response.json()
        self.token = json['token']
        self.user_id = str(json['user_id'])

    def get_user(self, user_id):
        """
        Fetch user details by user ID

        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        user = self.api.users(user_id).get()

        return mapper(User, user)

    def get_project(self, project_id):
        """
        Fetch project details by project ID

        :param project_id:
        :type project_id:
        :return:
        :rtype:
        """
        project = self.api.projects(project_id).get()

        return mapper(Project, project)

    def get_projects(self):
        """
        List projects for currently authenticated user

        :return:
        :rtype:
        """
        projects = self.api.projects().get(limit=-1)

        return [mapper(Project, dict(data=_)) for _ in projects['data']]

    def get_file(self, file_id):
        """
        Fetch file details by file ID

        :param file_id:
        :type file_id:
        :return:
        :rtype:
        """
        file_ = self.api.files(file_id).get()

        return mapper(File, file_)

    def get_files(self, project_id):
        """
        List files in project

        :param project_id:
        :type project_id:
        :return:
        :rtype:
        """
        files = self.api.files().get(projectId=project_id, limit=-1)

        return [mapper(File, dict(data=_)) for _ in files['data']]

    def get_analyses(self, file_id):
        """
        List analyses for file

        :param file_id:
        :type file_id:
        :return:
        :rtype:
        """
        out = list()

        file_ = self.api.files(file_id).get()
        analyses = file_['data']['relationships']['analyses']['data']
        for analysis_id in analyses:
            analysis = self.api.analyses(analysis_id['id']).get()

            vulnerability_id = analysis['data']['relationships']\
                ['vulnerability']['data']['id']
            analysis['data']['attributes']['vulnerability_id'] = \
                vulnerability_id

            analysis_obj = mapper(Analysis, analysis)
            out.append(analysis_obj)
        return out

    def get_vulnerability(self, vulnerability_id):
        """
        Get vulnerability by ID

        :param vulnerability_id:
        :type vulnerability_id: int
        :return:
        :rtype:
        """
        vulnerability = self.api.vulnerability(vulnerability_id).get()

        return mapper(Vulnerability, vulnerability)

    def upload_file(self, file):
        """
        Upload and scan a file

        :param file:
        :type file:
        """
        response = self.api.signed_url.get(
            content_type='application/octet-stream')

        url = response['url']
        data = file.read()
        requests.put(url, data=data)

        requests.post(
            urljoin(self.host, 'api/uploaded_file'),
            auth=(self.user_id, self.token),
            data=dict(
                file_key=response['file_key'],
                file_key_signed=response['file_key_signed']))

    def start_dynamic(self, file_id):
        """
        Start dynamic scan for a file

        :param file_id:
        :type file_id:
        """
        self.api.dynamic(file_id).get()

    def stop_dynamic(self, file_id):
        """
        Terminate dynamic scan for a file

        :param file_id: file ID
        :type file_id: int
        """
        self.api.dynamic_shutdown(file_id).get()

    def get_report(self, file_id, format):
        """
        Fetch analyses report for a file

        :param file_id: file ID
        :param format:
        :type file_id: int
        :type format: str
        :return:
        :rtype:
        """
        raise NotImplementedError()
