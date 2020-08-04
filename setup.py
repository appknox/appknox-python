# (c) 2017, XYSec Labs

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='appknox',
    version='4.1.0',
    description='Command-line interface & Python wrapper for the Appknox API',
    long_description=long_description,
    url='https://github.com/appknox/appknox-python',
    long_description_content_type="text/markdown",
    author='Appknox',
    author_email='engineering@appknox.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='appknox xysec rest api wrapper cli mobile security',
    packages=find_packages(),
    py_modules=['appknox'],
    entry_points='''
        [console_scripts]
        appknox=appknox.cli:main
    ''',
    install_requires=install_requires,
    extras_require={
        'dev': [''],
        'test': [''],
    },
)
