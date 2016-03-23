#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: setup.py
Version: 0.1
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2015-08-07
"""
__author__ = "dhilipsiva"
__status__ = "development"

"""
Python wrapper for Appknox's REST API
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

try:
    f = path.join(here, 'README.md')
    from pypandoc import convert
    long_description = convert(f, 'rst')
except IOError:
    print("Cannot read Readme.md file")
except ImportError:
    print(
        "pypandoc module not found, could not convert Markdown to RST")
    long_description = open(f, 'r').read()

setup(
    name='appknox',
    version='0.2.1',
    description="Python wrapper for Appknox's REST API",
    long_description=long_description,
    url='https://github.com/appknox/appknox-python',
    author='dhilipsiva',
    author_email='dhilipsiva@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='appknox xysec rest api wrapper',
    packages=find_packages(),
    py_modules=['appknox'],
    entry_points='''
        [console_scripts]
        appknox=appknox.cli:cli
    ''',
    install_requires=[
        'requests',
        'click',
    ],
    extras_require={
        'dev': [''],
        'test': [''],
    },
)
