# (c) 2017, XYSec Labs

import logging
import requests
import time

from functools import partial
from typing import List, Dict
from urllib.parse import urljoin

from appknox.exceptions import (
    OneTimePasswordError, CredentialError, AppknoxError, ReportError,
    OrganizationError
)
from appknox.mapper import (
    mapper_json_api, mapper_drf_api, Analysis, File, Project, User,
    Organization, Vulnerability, OWASP, PersonalToken
)

DEFAULT_API_HOST = 'https://api.appknox.com'
API_BASE = '/api'
JSON_API_HEADERS = {
    'Accept': 'application/vnd.api+json'
}
DRF_API_HEADERS = {
    'Accept': 'application/json'
}


class Cache(object):
    data = {}

    @classmethod
    def add(cls, data):
        data_type = data.get('type')
        data_id = data.get('id')
        if not data_type or not data_id:
            return

        cache_data_type = cls.data.get(data_type, {})
        cache_data_type[data_id] = data
        cls.data[data_type] = cache_data_type

    @classmethod
    def get(cls, data_type, data_id):
        cache_data_type = cls.data.get(data_type, {})
        return cache_data_type.get(data_id)

    @classmethod
    def delete(cls, data_type, data_id=None):
        if not data_id:
            cls.data[data_type] = {}
            return
        cache_data_type = cls.data.get(data_type, {})
        cache_data_type[data_id] = None

    @classmethod
    def clear(cls):
        cls.data = {}


class Appknox(object):
    """
    """

    def __init__(
        self, username: str = None, password: str = None, user_id: int = None,
        organization_id: int = None, token: str = None,
        access_token: str = None, host: str = DEFAULT_API_HOST,
        log_level: int = logging.INFO
    ):
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
        self.organization_id = organization_id
        self.token = token
        self.access_token = access_token

        if self.host is None:
            self.host = DEFAULT_API_HOST

        if self.access_token:
            token_header = {
                'Authorization': 'Token {}'.format(self.access_token)
            }
            self.json_api = ApiResource(
                host=self.host,
                headers={**JSON_API_HEADERS, **token_header}
            )
            self.drf_api = ApiResource(
                host=self.host,
                headers={**DRF_API_HEADERS, **token_header}
            )
            self.organization_id = self.get_organization_id()

        elif self.user_id and self.token:
            self.json_api = ApiResource(
                host=self.host,
                headers={**JSON_API_HEADERS},
                auth=(self.user_id, self.token)
            )
            self.drf_api = ApiResource(
                host=self.host,
                headers={**DRF_API_HEADERS},
                auth=(self.user_id, self.token)
            )
            self.organization_id = self.get_organization_id()

    def login(self, otp: int = None):
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

        self.json_api = ApiResource(
            host=self.host,
            headers={**JSON_API_HEADERS, **{
                'Authorization': 'Token {}'.format(self.access_token)
            }}
        )
        self.drf_api = ApiResource(
            host=self.host,
            headers={**DRF_API_HEADERS, **{
                'Authorization': 'Token {}'.format(self.access_token)
            }}
        )
        self.organization_id = self.get_organization_id()

    def get_organization_id(self, organization_id: int = None) -> int:
        """
        Return organization id if exists otherwise first entry of organizations
        """
        orgs = self.get_organizations()
        try:
            if organization_id:
                filtered_orgs = [o for o in orgs if o.id == organization_id]
            else:
                filtered_orgs = orgs
            return filtered_orgs[0].id
        except Exception:
            raise OrganizationError(
                'User doesn\'t have organization. Login Failed!'
            )

    def switch_organization(self, organization_id: int = None) -> bool:
        """
        Switch organization_id of client instance
        """
        org_id = int(organization_id)
        orgs = [o.id for o in self.get_organizations()]
        if len(orgs) and (org_id not in orgs):
            return False
        self.organization_id = organization_id
        return True

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
        return mapper_json_api(PersonalToken, access_token.json())

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
        user = self.json_api.users(user_id).get()

        return mapper_json_api(User, user)

    def get_project(self, project_id: int) -> Project:
        """
        Fetch project by project ID

        :param project_id: Project ID
        """
        project = self.json_api.projects(project_id).get()

        return mapper_json_api(Project, project)

    def paginated_data(self, response, mapper_class):
        initial_data = [mapper_json_api(
            mapper_class, dict(data=value)
        ) for value in response['data']]

        if not response.get('links'):
            return initial_data

        link = response['links']['next']

        while link is not None:
            resp = self.drf_api.direct_get(urljoin(self.host, link))
            link = resp['links']['next']
            initial_data += [mapper_json_api(
                mapper_class, dict(data=value)
            ) for value in resp['data']]

        return initial_data

    def paginated_drf_data(self, response, mapper_class):
        initial_data = [
            mapper_drf_api(mapper_class, value)
            for value in response['results']
        ]

        if not response.get('next'):
            return initial_data
        nxt = response['next']
        while nxt is not None:
            resp = self.drf_api.direct_get(nxt)
            nxt = resp['next']
            initial_data += [
                mapper_drf_api(mapper_class, value)
                for value in resp['results']
            ]

        return initial_data

    def get_organizations(self) -> List[Organization]:
        """
        List organizations for currently authenticated user
        """
        organizations = self.drf_api.organizations().get(limit=-1)
        return self.paginated_drf_data(organizations, Organization)

    def get_projects(
        self, platform: int = None, package_name: str = '', search: str = ''
    ) -> List[Project]:
        """
        List projects for currently authenticated user
        in the given organizations
        """
        projects = self.drf_api[
            'organizations/{}/projects'.format(self.organization_id)
        ]().get(platform=platform, package_name=package_name, q=search)

        return self.paginated_drf_data(projects, Project)

    def get_file(self, file_id: int) -> File:
        """
        Fetch file by file ID

        :param file_id: File ID
        """
        file_ = self.json_api.files(file_id).get()

        return mapper_json_api(File, file_)

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

        files = self.json_api.files().get(**filter_options)

        return self.paginated_data(files, File)

    def get_analyses(self, file_id: int) -> List[Analysis]:
        """
        List analyses for file

        :param file_id: File ID
        """
        out = list()
        file_ = file_ = self.json_api.files(file_id).get()
        for d in file_.get('included', []):
            Cache.add(d)

        analyses = file_['data']['relationships']['analyses']['data']
        for analysis_id in analyses:
            analysis = Cache.get('analyses', analysis_id['id'])
            analysis = {
                'data': analysis
            }
            if not analysis:
                analysis = self.json_api.analyses(analysis_id['id']).get()
                Cache.add(analysis['data'])
                for d in analysis.get('included', []):
                    Cache.add(d)

            vuln_id = analysis[
                'data']['relationships']['vulnerability']['data']['id']
            analysis['data']['attributes']['vulnerability-id'] = vuln_id

            out.append(mapper_json_api(Analysis, analysis))
        return out

    def get_vulnerability(self, vulnerability_id: int) -> Vulnerability:
        """
        Fetch vulnerability by vulnerability ID

        :param vulnerability_id: vulnerability ID
        """
        vulnerability = self.json_api.vulnerabilities(vulnerability_id).get()

        return mapper_json_api(Vulnerability, vulnerability)

    def get_owasp(self, owasp_id: str) -> OWASP:
        """
        Fetch OWASP by ID

        :param owasp_id: OWASP ID
        """
        cache_data = Cache.get('owasp', owasp_id)
        if cache_data:
            return mapper_json_api(OWASP, {
                'data': cache_data
            })
        owasp = self.json_api.owasps(owasp_id).get()
        Cache.add(owasp.get('data', {}))

        return mapper_json_api(OWASP, owasp)

    def upload_file(self, file_data: str):
        """
        Upload and scan a package

        :param file: Package file content to be uploaded and scanned
        """
        response = self.drf_api[
            'organizations/{}/upload_app'.format(self.organization_id)
        ]().get()
        url = response['url']
        requests.put(url, data=file_data)
        self.drf_api[
            'organizations/{}/upload_app'.format(self.organization_id)
        ]().post(
            data=dict(
                file_key=response['file_key'],
                file_key_signed=response['file_key_signed'],
                url=response['url']
            )
        )

    def rescan(self, file_id: int):
        """
        Start a rescan for a file id

        :param filed_id: File ID
        """
        self.drf_api['rescan']().post(
            data=dict(
                file_id=file_id,
            )
        )

    def get_report(
            self, file_id, format: str = 'json', language: str = 'en') -> str:
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

        return self.json_api.report(file_id).get(
            format=format, language=language
        )


class ApiResource(object):
    def __init__(
        self, host: str = DEFAULT_API_HOST, headers: object = None,
        auth: Dict[str, str] = None
    ):
        self.host = host
        self.headers = {**headers}
        self.auth = auth

        self.endpoint = urljoin(host, API_BASE)

    def __getitem__(self, resource):
        return partial(self.set_endpoint, resource)

    def __getattr__(self, resource):
        return partial(self.set_endpoint, resource)

    def set_endpoint(self, resource, resource_id=None):
        self.endpoint = '{}/{}'.format(urljoin(self.host, API_BASE), resource)
        if resource_id:
            self.endpoint += '/{}'.format(str(resource_id))
        return self

    def get(self, **kwargs):
        resp = requests.get(
            self.endpoint, headers=self.headers, auth=self.auth,
            params=kwargs
        )
        return resp.json()

    def post(self, data, content_type=None, **kwargs):
        resp = requests.post(
            self.endpoint, headers=self.headers, auth=self.auth,
            params=kwargs, data=data
        )
        return resp.json()

    def direct_get(self, url, **kwargs):
        resp = requests.get(
            url, headers=self.headers, auth=self.auth, params=kwargs
        )
        return resp.json()
