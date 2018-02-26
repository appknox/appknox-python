# (c) 2017, XYSec Labs

import logging
import requests
import time

from functools import partial
from typing import List, Dict
from urllib.parse import urljoin

from appknox.exceptions import OneTimePasswordError, CredentialError, \
    AppknoxError, ReportError
from appknox.mapper import mapper, Analysis, File, Project, User, \
    Vulnerability, PersonalToken

DEFAULT_API_HOST = 'https://api.appknox.com'
API_BASE = '/api'
JSON_API_HEADERS = {
    'Content-Type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json'
}


class Appknox(object):
    """
    """

    def __init__(self, username: str=None, password: str=None,
                 user_id: int=None, token: str=None, access_token: str=None,
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
        self.access_token = access_token

        if self.access_token:
            self.api = ApiResource(
                host=self.host,
                headers={
                    'Authorization': 'Token {}'.format(self.access_token)
                }
            )
        elif self.user_id and self.token:
            self.api = ApiResource(
                host=self.host,
                auth=(self.user_id, self.token)
            )

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
        self.access_token = self.generate_access_token().key
        self.api = ApiResource(
            host=self.host,
            headers={'Authorization': 'Token {}'.format(self.access_token)}
        )

    def generate_access_token(self):
        """
        Generates personal access token
        """
        access_token = requests.post(
            urljoin(self.host, 'api/personaltokens'),
            auth=(self.user_id, self.token),
            data={
                'name': 'appknox-python for {} @{}'.format(
                    self.username, str(int(time.time()))
                )
            }
        )
        return mapper(PersonalToken, access_token.json())

    def revoke_access_token(self):
        """
        Revokes existing personal access token
        """
        resp = requests.get(
            urljoin(self.host, 'api/personaltokens?key=' + self.access_token),
            auth=(self.user_id, self.token)
        )
        resp_json = resp.json()
        personal_token = next((p for p in resp_json.get('data')), None)
        if not personal_token:
            return

        token_id = personal_token['id']
        return requests.delete(
            urljoin(self.host, 'api/personaltokens/' + token_id),
            auth=(self.user_id, self.token)
        )

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

    def paginated_data(self, response, mapper_class):
        initial_data = [mapper(
            mapper_class, dict(data=value)
        ) for value in response['data']]

        if not response.get('links'):
            return initial_data

        link = response['links']['next']

        while link is not None:
            resp = requests.get(
                urljoin(self.host, link),
                auth=(self.user_id, self.token)
            )
            resp_json = resp.json()
            link = resp_json['links']['next']
            initial_data += [mapper(
                mapper_class, dict(data=value)
            ) for value in resp_json['data']]

        return initial_data

    def get_projects(
        self, platform: int = -1, package_name: str = ''
    ) -> List[Project]:
        """
        List projects for currently authenticated user
        """
        projects = self.api.projects().get(
            limit=-1, platform=platform, query=package_name
        )

        return self.paginated_data(projects, Project)

    def get_file(self, file_id: int) -> File:
        """
        Fetch file by file ID

        :param file_id: File ID
        """
        file_ = self.api.files(file_id).get()

        return mapper(File, file_)

    def get_files(
        self, project_id: int, version_code: int = None
    ) -> List[File]:
        """
        List files in project

        :param project_id: Project ID
        """
        filter_options = {
            'projectId': project_id,
            'limit': -1
        }
        if version_code:
            filter_options['version_code'] = version_code

        files = self.api.files().get(**filter_options)

        return self.paginated_data(files, File)

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


class ApiResource(object):
    def __init__(
        self, host: str=DEFAULT_API_HOST,
        headers: object=None, auth: Dict[str, str]=None
    ):
        self.host = host
        self.headers = {**JSON_API_HEADERS, **headers}
        self.auth = auth

        self.endpoint = urljoin(host, API_BASE)

    def __getattr__(self, resource):
        return partial(self.set_endpoint, resource)

    def set_endpoint(self, resource, resource_id=None):
        self.endpoint = '{}/{}'.format(urljoin(self.host, API_BASE), resource)
        if resource_id:
            self.endpoint += '/{}'.format(str(resource_id))
        return self

    def get(self, *args, **kwargs):
        try:
            resp = requests.get(
                self.endpoint, headers=self.headers, auth=self.auth,
                params=kwargs
            )
            return resp.json()
        except Exception as e:
            return {}
