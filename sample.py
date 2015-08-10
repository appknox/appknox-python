#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: sample.py
Version: 0.1
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2015-08-10
"""
__author__ = "dhilipsiva"
__status__ = "development"

"""
This is for sample usage
"""
import logging

logger = logging.getLogger("appknox")
logger.setLevel(10)

from appknox import AppknoxClient

appknox_client = AppknoxClient(username='dhilipsiva', password='password')
logger.debug('Token: %s', appknox_client.token)
print appknox_client.submit_url("market://com.flipkart.android")
# Upload File
# _file = open("sample.apk")
# print appknox_client.upload_file(_file)
