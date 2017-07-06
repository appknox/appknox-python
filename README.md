[![PyPI version](https://badge.fury.io/py/appknox.svg)](https://badge.fury.io/py/appknox)
[![Build Status](https://travis-ci.org/appknox/appknox-python.svg)](https://travis-ci.org/appknox/appknox-python)
[![Join the chat at https://gitter.im/appknox/appknox-python](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/appknox/appknox-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# appknox-python

Command-line interface & Python wrapper for the Appknox API.

## Installation

appknox-python is officially supported on python 3.5. pip is the recommended way to install appknox-python.

```
pip install appknox
```

Python API documentation is available [here](http://appknox.org/appknox-python/).

## Quickstart

```
$ appknox login
Username: viren
Password:
Logged in to https://api.appknox.com

$ appknox projects
  id  created_on             file_count  package_name                     platform  updated_on
----  -------------------  ------------  -----------------------------  ----------  -------------------
   3  2017-06-23 07:19:26             3  org.owasp.goatdroid.fourgoats           0  2017-06-23 07:26:55
   4  2017-06-27 08:27:54             2  com.appknox.mfva                        0  2017-06-27 08:30:04

$ appknox files 4
  id  name      version    version_code
----  ------  ---------  --------------
   6  MFVA            1               6
   7  MFVA            1               6
```

## Usage

```
Usage: appknox [OPTIONS] COMMAND [ARGS]...

  Command line wrapper for the Appknox API

Options:
  -v, --verbose  Specify log verbosity.
  --help         Show this message and exit.

Commands:
  analyses       List analyses for file
  dynamic_start  Start dynamic scan for file
  dynamic_stop   Stop dynamic scan for file
  files          List files for project
  login          Log in and save session credentials
  logout         Delete session credentials
  projects       List projects
  report         Download report for file
  upload         Upload and scan package
  vulnerability  Get vulnerability
  whoami         Show session info
```

---

License: MIT
