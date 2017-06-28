# (c) 2017, XYSec Labs

import logging
import requests
import slumber

from typing import List
from urllib.parse import urljoin

from appknox.exceptions import OneTimePasswordError, CredentialError, \
    AppknoxError, ReportError
from appknox.mapper import mapper, Analysis, File, Project, User, Vulnerability

DEFAULT_API_HOST = 'https://api.appknox.com'


class Appknox(object):
    """
    Appknox class provides an easy access to the Appknox API.

    Instances of this class can be used to interact with the Appknox scanner.
    To obtain an instance of this class:

    .. code-block:: python

        import appknox
        appknox = appknox.Appknox(
                    username='USERNAME',
                    password='PASSWORD',
                    host='HOST')

    To perform authentication:

    .. code-block:: python

        appknox.login(otp=000000)

    ``otp`` is required for accounts with multi-factor authentication.

    """

    def __init__(self, username: str=None, password: str=None,
                 user_id: int=None, token: str=None,
                 host: str=DEFAULT_API_HOST, log_level: int=logging.INFO):
        """
        Initialise Appknox client

        :param username: Username used to authenticate and fetch token
        :param password: Password used to authenticate and fetch token
        :param user_id: User ID. Set this only if a token is available
        :param token: Token. Set this only if a token is available
        :param host: API host. By default, https://api.appknox.com

        If a token is not available, set ``username`` and ``password`` and use
        the ``login`` method to authenticate. Otherwise, ``user_id`` and
        ``token`` can be used.
        """
        logging.basicConfig(level=log_level)

        self.host = host
        self.username = username
        self.password = password
        self.user_id = user_id
        self.token = token
        self.endpoint = urljoin(self.host, 'api/')

        if self.user_id and self.token:
            self.api = slumber.API(self.endpoint,
                                   auth=(self.user_id, self.token),
                                   append_slash=False)

    def login(self, otp: int=None):
        """
        Authenticate with server and create session

        :param otp: One-time password, if account has MFA enabled
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

        self.api = slumber.API(self.endpoint, auth=(self.user_id, self.token),
                               append_slash=False)

    def get_user(self, user_id: int) -> User:
        """
        Fetch user by user ID

        :param user_id: User ID
        """
        user = self.api.users(user_id).get()

        return mapper(User, user)

    def get_project(self, project_id: int) -> Project:
        """
        Fetch project by project ID

        :param project_id: Project ID
        """
        project = self.api.projects(project_id).get()

        return mapper(Project, project)

    def get_projects(self) -> List[Project]:
        """
        List projects for currently authenticated user
        """
        projects = self.api.projects().get(limit=-1)

        return [mapper(Project, dict(data=_)) for _ in projects['data']]

    def get_file(self, file_id: int) -> File:
        """
        Fetch file by file ID

        :param file_id: File ID
        """
        file_ = self.api.files(file_id).get()

        return mapper(File, file_)

    def get_files(self, project_id: int) -> List[File]:
        """
        List files in project

        :param project_id: Project ID
        """
        files = self.api.files().get(projectId=project_id, limit=-1)

        return [mapper(File, dict(data=_)) for _ in files['data']]

    def get_analyses(self, file_id: int) -> List[Analysis]:
        """
        List analyses for file

        :param file_id: File ID
        """
        out = list()

        file_ = self.api.files(file_id).get()
        analyses = file_['data']['relationships']['analyses']['data']

        for analysis_id in analyses:
            analysis = self.api.analyses(analysis_id['id']).get()

            vuln_id = analysis[
                'data']['relationships']['vulnerability']['data']['id']
            analysis['data']['attributes']['vulnerability-id'] = vuln_id

            out.append(mapper(Analysis, analysis))
        return out

    def get_vulnerability(self, vulnerability_id: int) -> Vulnerability:
        """
        Fetch vulnerability by vulnerability ID

        :param vulnerability_id: vulnerability ID
        """
        vulnerability = self.api.vulnerabilities(vulnerability_id).get()

        return mapper(Vulnerability, vulnerability)

    def upload_file(self, file):
        """
        Upload and scan a package

        :param file: Package file to be uploaded and scanned
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

    def start_dynamic(self, file_id: int):
        """
        Start dynamic scan for a file

        :param file_id: File ID
        """
        self.api.dynamic(file_id).get()

    def stop_dynamic(self, file_id: int):
        """
        Terminate dynamic scan for a file

        :param file_id: File ID
        """
        self.api.dynamic_shutdown(file_id).get()

    def get_report(
            self, file_id, format: str='json', language: str='en') -> str:
        """
        Fetch analyses report for a file

        :param file_id: File ID
        :param format: Report format (supported 'json', 'pdf'). Default 'json'
        :param language: Report language (supported 'en', 'ja'). Default 'en'
        :type file_id: int
        :type format: str
        :type language: str
        :return:
        """
        if format not in ['json', 'pdf']:
            raise ReportError('Unsupported format')
        if language not in ['en', 'ja']:
            raise ReportError('Unsupported language')

        return self.api.report(file_id).get(format=format, language=language)
