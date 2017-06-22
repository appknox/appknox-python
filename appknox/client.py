import logging
import requests

from urllib.parse import urlencode, urljoin

from appknox.exceptions import OneTimePasswordError, CredentialError, \
    ResponseError, InvalidReportTypeError
from appknox.defaults import DEFAULT_VULNERABILITY_LANGUAGE, \
    DEFAULT_API_HOST, DEFAULT_REPORT_LANGUAGE, DEFAULT_OFFSET, \
    DEFAULT_LIMIT, DEFAULT_REPORT_FORMAT


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

    def login(self, otp=None):
        """
        :param otp: One-time password, if account has MFA enabled
        :type otp: int
        """

        if not self.username or not self.password:
            raise CredentialError('Both username and password are required')

        login_url = '{}/api/login'.format(self.host)
        data = {
            'username': self.username,
            'password': self.password,
        }

        if otp:
            data['otp'] = str(otp)

        logging.debug('Request {}: {}'.format(login_url, data))
        response = requests.post(login_url, data=data)

        if response.status_code == 401:
            raise OneTimePasswordError(response.json()['message'])
        elif response.status_code == 403:
            raise CredentialError(response.json()['message'])

        json = response.json()
        self.token = json['token']
        self.user_id = str(json['user_id'])

    def _request(self, method, endpoint, data=dict()):
        url = urljoin(urljoin(self.host, '/api/'), endpoint)
        logging.debug('Request {}: {}'.format(url, data))
        response = method(url, data=data, auth=(self.user_id, self.token))

        if response.status_code < 200 or response.status_code > 299:
            raise ResponseError(response.content)

        try:
            return response.json()
        except ValueError:
            logging.debug('Response has no valid JSON')
            return response.content.decode()

    def get_user(self, user_id):
        url = 'users/{}'.format(user_id)
        response = self._request(requests.get, url)

        return response

    def upload_file(self, _file):
        url = 'signed_url'
        data = {'content_type': 'application/octet-stream'}
        response = self._request(requests.get, url, data)

        url = response['url']
        data=_file.read()
        response = requests.put(url, data=data)

        url = 'uploaded_file'
        data = {
            'file_key': json['file_key'],
            'file_key_signed': json['file_key_signed']}
        response = self._request(requests.post, url, data=data, auth=(self.user_id, self.token))

        return response

    def get_project(self, project_id):
        url = 'projects/{}'.format(project_id)
        response = self._request(requests.get, url)

        return response

    def list_projects(self):
        url = 'projects'
        response = self._request(requests.get, url)

        return response

    def get_file(self, file_id):
        pass

    def list_files(self, project_id):
        pass

    def start_dynamic(self, file_id):
        pass

    def stop_dynamic(self, file_id):
        pass

    def list_analyses(self, file_id):
        pass

    def get_report(self, file_id):
        pass
