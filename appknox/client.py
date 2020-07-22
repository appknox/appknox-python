# (c) 2017, XYSec Labs

import logging
import requests
import time

from functools import partial, lru_cache
from typing import List, Dict
from urllib.parse import urljoin

from appknox.exceptions import (
    OneTimePasswordError, CredentialError, AppknoxError,
    OrganizationError, UploadError, SubmissionNotFound,
    SubmissionError, SubmissionFileTimeoutError, RescanError
)
from appknox.mapper import (
    mapper_json_api, mapper_drf_api, Analysis, File, Project, User,
    Organization, Vulnerability, OWASP, PCIDSS, PersonalToken, Submission,
    Whoami
)

DEFAULT_API_HOST = 'https://api.appknox.com'
API_BASE = '/api'
JSON_API_HEADERS = {
    'Accept': 'application/vnd.api+json'
}
DRF_API_HEADERS = {
    'Accept': 'application/json'
}


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

    def get_whoami(self) -> Whoami:
        """
        Show session info
        """
        whoami = self.drf_api.me().get()
        return mapper_drf_api(Whoami, whoami)

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

    def get_project(self, project_id: int) -> Project:
        """
        Fetch project by project ID

        :param project_id: Project ID
        """
        project = self.drf_api[
            'v2/projects/{}'.format(project_id)
        ]().get()
        return mapper_drf_api(Project, project)

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

    def get_last_file(self, project_id: int, version_code: int = None) -> File:
        """
        Fetch latest file for the project

        :param project_id: Project ID
        """
        files = self.drf_api[
            'projects/{}/files'.format(project_id)
        ]().get(version_code=version_code, limit=1).get('results', [])
        if not files:
            return None
        return mapper_drf_api(File, files[0])

    def get_file(self, file_id: int) -> File:
        """
        Fetch file by file ID
        :param file_id: File ID
        """
        file = self.drf_api[
            'v2/files/{}'.format(file_id)
        ]().get()
        return mapper_drf_api(File, file)

    def get_files(
        self, project_id: int, version_code: int = None
    ) -> List[File]:
        """
        List files in project

        :param project_id: Project ID
        """
        files = self.drf_api[
            'projects/{}/files'.format(project_id)
        ]().get(version_code=version_code)
        return self.paginated_drf_data(files, File)

    def get_analyses(self, file_id: int) -> List[Analysis]:
        """
        List analyses for file

        :param file_id: File ID
        """
        analyses = self.drf_api[
            'v2/files/{}/analyses'.format(file_id)
        ]().get()
        return self.paginated_drf_data(analyses, Analysis)

    @lru_cache(maxsize=1)
    def get_vulnerabilities(self) -> List[Vulnerability]:
        total_vulnerabilities = self.drf_api[
            'v2/vulnerabilities'
        ]().get(limit=1)['count']  # limit is 1 just to get total count
        vulnerabilities_raw = self.drf_api['v2/vulnerabilities']().get(
            limit=total_vulnerabilities+1
        )
        vulnerabilities = self.paginated_drf_data(
            vulnerabilities_raw, Vulnerability
        )
        return vulnerabilities

    def get_vulnerability(self, vulnerability_id: int) -> Vulnerability:
        """
        Fetch vulnerability by vulnerability ID

        :param vulnerability_id: vulnerability ID
        """
        vulnerabilities = self.get_vulnerabilities()
        vulnerability = next(
            (x for x in vulnerabilities if x.id == vulnerability_id),
            None
        )
        if vulnerability:
            return vulnerability

        vulnerability = self.drf_api[
            'v2/vulnerabilities'
        ](vulnerability_id).get()
        return mapper_drf_api(Vulnerability, vulnerability)

    @lru_cache(maxsize=1)
    def get_owasps(self) -> List[OWASP]:
        owasps_raw = self.drf_api['v2/owasps']().get()
        owasps = self.paginated_drf_data(
            owasps_raw, OWASP
        )
        return owasps

    def get_owasp(self, owasp_id: str) -> OWASP:
        """
        Fetch OWASP by ID

        :param owasp_id: OWASP ID
        """
        owasps = self.get_owasps()
        owasp = next(
            (x for x in owasps if x.id == owasp_id),
            None
        )
        if owasp:
            return owasp

        owasp = self.drf_api['v2/owasps'](owasp_id).get()
        return mapper_drf_api(OWASP, owasp)

    @lru_cache(maxsize=1)
    def get_pcidsses(self) -> List[PCIDSS]:
        pcidsss_raw = self.drf_api['v2/pcidsses']().get()
        pcidsss = self.paginated_drf_data(
            pcidsss_raw, PCIDSS
        )
        return pcidsss

    def get_pcidss(self, pcidss_id: str) -> PCIDSS:
        """
        Fetch pcidss by ID

        :param pcidss_id: pcidss ID
        """
        pcidsses = self.get_pcidsses()
        pcidss = next(
            (x for x in pcidsses if x.id == pcidss_id),
            None
        )
        if pcidss:
            return pcidss

        pcidss = self.drf_api['v2/pcidsses'](pcidss_id).get()
        return mapper_drf_api(PCIDSS, pcidss)

    def upload_file(self, file_data: str) -> int:
        """
        Upload and scan a package and returns the file_id

        :param file: Package file content to be uploaded and scanned
        """
        response = self.drf_api[
            'organizations/{}/upload_app'.format(self.organization_id)
        ]().get()
        url = response['url']
        requests.put(url, data=file_data)
        response2 = self.drf_api[
            'organizations/{}/upload_app'.format(self.organization_id)
        ]().post(
            data=dict(
                file_key=response['file_key'],
                file_key_signed=response['file_key_signed'],
                url=response['url']
            )
        )
        submission_id = response2['submission_id']
        try:
            file_id = self.poll_for_file_from_submission_id(submission_id)
        except (SubmissionNotFound, SubmissionError):
            raise UploadError('Something went wrong, try uploading the\
             file again.')
        return file_id

    def poll_for_file_from_submission_id(self, submission_id: int) -> int:
        """
        Using the submission id, keep checking its status.
        Returns file instance when it's available

        :param submission_id: The ID of the submission object
         created for the scan

         :return: The File ID
        """
        file = None
        timeout = time.time() + 10
        while (file is None):
            submission = self.drf_api.submissions(submission_id).get()
            if submission.get('detail') == 'Not found.':
                raise SubmissionNotFound()
            submission_obj = mapper_drf_api(Submission, submission)
            file = submission_obj.file
            if submission_obj.reason:
                raise SubmissionError(submission_obj.reason)
            if time.time() > timeout:
                raise SubmissionFileTimeoutError()
        return file

    def recent_uploads(self) -> List[Submission]:
        """
        List details of recent file uploads
        """
        submissions = self.drf_api.submissions().get()

        return self.paginated_drf_data(submissions, Submission)[0:10]

    def rescan(self, file_id: int) -> int:
        """
        Start a rescan for a file id

        :param filed_id: File ID

        :return: The ID of the File created in rescan
        """
        endpoint = 'v2/files/{}/rescan'.format(file_id)
        response = self.drf_api[endpoint]().post(
            data=dict()

        )
        submission_id = response['submission_id']
        try:
            file = self.poll_for_file_from_submission_id(submission_id)
        except (SubmissionNotFound, SubmissionError):
            raise RescanError('Something went wrong, retry rescan')
        return file

    # def get_report(
    #         self, file_id, format: str = 'json', language: str = 'en') ->
    #         str:
    #     """
    #     Fetch analyses report for a file
    #     :param file_id: File ID
    #     :param format: Report format (supported 'json', 'pdf'). Default
    #                    'json'
    #     :param language: Report language (supported 'en', 'ja'). Default 'en'
    #     :type file_id: int
    #     :type format: str
    #     :type language: str
    #     :return:
    #     """
    #     if format not in ['json', 'pdf']:
    #         raise ReportError('Unsupported format')
    #     if language not in ['en', 'ja']:
    #         raise ReportError('Unsupported language')

    #     return self.json_api.report(file_id).get(
    #         format=format, language=language
    #     )


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
