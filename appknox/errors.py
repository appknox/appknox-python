#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: errors.py
Version: 0.1
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2015-08-07
"""
__author__ = "dhilipsiva"
__status__ = "development"

"""
Just a list of errors
"""


class AppknoxError(Exception):

    def __init__(self, error_detail):
        super(AppknoxError, self).__init__()
        self.error_detail = error_detail

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.error_detail)


class MissingCredentialsError(AppknoxError):

    def __init__(self):
        super(MissingCredentialsError, self).__init__(
            "Please provide either `username/password`")


class InvalidCredentialsError(AppknoxError):

    def __init__(self):
        super(InvalidCredentialsError, self).__init__(
            "Your username / password pair is invalid."
            " Please check username & password")


class ResponseError(AppknoxError):

    def __init__(self, message):
        super(ResponseError, self).__init__(
            "Server Error Occured: %s" % message)


class InvalidReportTypeError(AppknoxError):

    def __init__(self, message):
        super(InvalidReportTypeError, self).__init__(
            " %s" % message)
