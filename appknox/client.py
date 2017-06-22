import logging
import requests

from urllib.parse import urlencode, urljoin

from appknox.exceptions import OTPRequiredError, MissingCredentialsError, \
    InvalidCredentialsError, ResponseError, InvalidReportTypeError
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
            raise MissingCredentialsError

        login_url = '{}/api/login'.format(self.host)
        data = {
            'username': self.username,
            'password': self.password,
        }

        if otp:
            data['otp'] = otp

        logging.debug('Request {}: {}'.format(login_url, data))
        response = requests.post(login_url, data=data)

        if response.status_code == 401:
            raise OTPRequiredError
        elif response.status_code == 403:
            raise InvalidCredentialsError

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

    def current_user(self):
        url = 'users/' + str(self.user_id)
        return self._request(requests.get, url)

    def upload_file(self, _file):
        """
        :param _file: package file to upload
        :type _file: a python `file` object
        """

        data = {'content_type': 'application/octet-stream'}
        json = self._request(requests.get, 'signed_url', data)
        url = json['url']

        response = requests.put(url, data=_file.read())
        data = {
            'file_key': json['file_key'],
            'file_key_signed': json['file_key_signed'],
        }

        url = '%s/uploaded_file' % self.host
        response = requests.post(
            url, data=data, auth=(self.user_id, self.token))

        return response.json()

    def project_get(self, project_id):
        """
        :param project_id: Project ID
        :type project_id: int
        """
        url = 'projects/' + str(project_id)
        return self._request(requests.get, url)

    def project_list(
            self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET):
        """
        return list of projects
        """
        params = {'limit': limit, 'offset': offset}
        url = 'projects?%s' % (urlencode(params))
        return self._request(requests.get, url)

    def file_get(self, file_id):
        """
        get file details with file id
        """
        url = 'files/' + str(file_id)
        return self._request(requests.get, url)

    def file_list(
            self, project_id, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET):
        """
        return list of files for a project
        """
        params = {'projectId': project_id, 'offset': offset, 'limit': limit}
        url = 'files?%s' % (urlencode(params))
        return self._request(requests.get, url)

    def dynamic_start(self, file_id):
        url = 'dynamic/{}'.format(str(file_id))
        return self._request(requests.get, url)

    def dynamic_stop(self, file_id):
        url = 'dynamic_shutdown/{}'.format(str(file_id))
        return self._request(requests.get, url)

    def dynamic_restart(self, file_id):
        self.dynamic_stop(file_id)
        return self.dynamic_start(file_id)

    def analyses_list(self, file_id):
        url = 'files/' + str(file_id)
        return self._request(requests.get, url)

    def report(
            self, file_id, format_type=DEFAULT_REPORT_FORMAT,
            language=DEFAULT_REPORT_LANGUAGE):
        if format_type not in ['json', 'pdf']:
            raise InvalidReportTypeError('Invalid format type')
        if language not in ['en', 'ja']:
            raise InvalidReportTypeError('Unsupported language')

        params = {'format': format_type, 'language': language}
        url = 'report/%s?%s' % (str(file_id), urlencode(params))
        return self._request(requests.get, url)

    def payment(self, card):
        data = {'card', card}
        return self._request(requests.post, 'stripe_payment', data)

    def vulnerability(
            self, vulnerability_id, language=DEFAULT_VULNERABILITY_LANGUAGE):
        url = 'vulnerabilities/' + str(vulnerability_id)
        return self._request(requests.get, url)
