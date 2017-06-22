# (c) 2015-217, XYSec Labs


class AppknoxError(Exception):

    def __init__(self, error_detail):
        super(AppknoxError, self).__init__()
        self.error_detail = error_detail

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.error_detail)


class MissingCredentialsError(AppknoxError):

    def __init__(self):
        super(MissingCredentialsError, self).__init__(
            'Username and password are required')


class InvalidCredentialsError(AppknoxError):

    def __init__(self):
        super(InvalidCredentialsError, self).__init__(
            'Username or/and password is invalid')


class OTPRequiredError(AppknoxError):

    def __init__(self):
        super(OTPRequiredError, self).__init__(
            'One-time password is required')


class ResponseError(AppknoxError):

    def __init__(self, message):
        super(ResponseError, self).__init__('Server error: {}'.format(message))


class InvalidReportTypeError(AppknoxError):

    def __init__(self, message):
        super(InvalidReportTypeError, self).__init__(' {}'.format(message))
