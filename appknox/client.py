# (c) 2017, XYSec Labs

import logging
import requests
import slumber

from urllib.parse import urljoin

from appknox.exceptions import OneTimePasswordError, CredentialError, \
    AppknoxError
from appknox.defaults import DEFAULT_API_HOST
from appknox.mapper import mapper, Analysis, File, Project, User, Vulnerability


class Appknox(object):
    """
    Appknox class provides an easy access to the Appknox API

    Instances of this class can be used to interact with the Appknox scanner.
    To obtain an instance of this class:

    .. code-block: python

        import appknox
        appknox = appknox.Appknox(username='USERNAME', password='PASSWORD',
                                  host='HOST')

    """

    def __init__(self, username=None, password=None, user_id=None, token=None,
                 host=DEFAULT_API_HOST, log_level=logging.INFO):
        """
        Initialise an Appknox client

        :param username: Username used to authenticate and fetch token
        :param password: Password used to authenticate and fetch token
        :param user_id: User ID. Set this only if a token is available
        :param token: Token. Set this only if a token is available
        :param host: API host. By default, https://api.appknox.com
        :type username: str
        :type password: str
        :type user_id: int
        :type token: str
        :type host: str

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

    def login(self, otp=None):
        """
        Authenticate with server and fetch a token

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

        self.api = slumber.API(self.endpoint, auth=(self.user_id, self.token),
                               append_slash=False)

    def get_user(self, user_id):
        """
        Fetch user by user ID

        :param user_id: User ID
        :type user_id: int
        :return: :class`.User`
        """
        user = self.api.users(user_id).get()

        return mapper(User, user)

    def get_project(self, project_id):
        """
        Fetch project by project ID

        :param project_id: Project ID
        :type project_id: int
        :return: :class`.Project`
        """
        project = self.api.projects(project_id).get()

        return mapper(Project, project)

    def get_projects(self):
        """
        List projects for currently authenticated user

        :return: List of :class`.Project`
        """
        projects = self.api.projects().get(limit=-1)

        return [mapper(Project, dict(data=_)) for _ in projects['data']]

    def get_file(self, file_id):
        """
        Fetch file by file ID

        :param file_id: File ID
        :type file_id: int
        :return: :class`.File`
        """
        file_ = self.api.files(file_id).get()

        return mapper(File, file_)

    def get_files(self, project_id):
        """
        List files in project

        :param project_id: Project ID
        :type project_id: int
        :return: List of :class`.File`
        """
        files = self.api.files().get(projectId=project_id, limit=-1)

        return [mapper(File, dict(data=_)) for _ in files['data']]

    def get_analyses(self, file_id):
        """
        List analyses for file

        :param file_id: File ID
        :type file_id: int
        :return: List of :class`.Analysis`
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

    def get_vulnerability(self, vulnerability_id):
        """
        Fetch vulnerability by vulnerability ID

        :param vulnerability_id: vulnerability ID
        :type vulnerability_id: int
        :return: :class`.Vulnerability`
        """
        vulnerability = self.api.vulnerabilities(vulnerability_id).get()

        return mapper(Vulnerability, vulnerability)

    def upload_file(self, file):
        """
        Upload and scan a package

        :param file: Package file to be uploaded and scanned
        :type file: a :class`File` object
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

        :param file_id: File ID
        :type file_id: int
        """
        self.api.dynamic(file_id).get()

    def stop_dynamic(self, file_id):
        """
        Terminate dynamic scan for a file

        :param file_id: File ID
        :type file_id: int
        """
        self.api.dynamic_shutdown(file_id).get()

    def get_report(self, file_id, format):
        """
        Fetch analyses report for a file

        :param file_id: File ID
        :param format: Desired format of report
        :type file_id: int
        :type format: str
        :return:
        :rtype:
        """
        raise NotImplementedError()
