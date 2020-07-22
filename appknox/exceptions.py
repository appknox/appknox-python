# (c) 2015-217, XYSec Labs


class AppknoxError(Exception):

    def __init__(self, message='-'):
        super(AppknoxError, self).__init__()
        self.message = message

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.message)


class CredentialError(AppknoxError):
    pass


class OneTimePasswordError(AppknoxError):
    pass


# class ReportError(AppknoxError):
#     pass


class OrganizationError(AppknoxError):
    pass


class UploadError(AppknoxError):
    pass


class SubmissionNotFound(AppknoxError):
    pass


class SubmissionError(AppknoxError):
    pass


class SubmissionFileTimeoutError(AppknoxError):
    pass


class RescanError(AppknoxError):
    pass
