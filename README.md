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

Documentation is available [here](http://appknox.org/appknox-python/).

## Quickstart

```python
In [1]: import appknox

# Create an Appknox instance and login
In [2]: client = appknox.Appknox(username='viren', password='foobar')
In [3]: client.login()

# List projects for authenticated user
In [4]: client.get_projects()
Out[4]:
[Project(id=3, created_on='2017-06-23 07:19:26.720829+00:00', file_count=3,
         package_name='org.owasp.goatdroid.fourgoats', platform=0,
         updated_on='2017-06-23 07:26:55.456744+00:00'),
 Project(id=4, created_on='2017-06-27 08:27:54.486226+00:00', file_count=1,
         package_name='com.appknox.mfva', platform=0,
         updated_on='2017-06-27 08:27:54.637432+00:00')]

# List files within a project
In [5]: client.get_files(4)
Out[5]: [File(id=6, name='MFVA', version='1.0', version_code='6')]

# Upload a file and commence static scan
In [6]: client.upload_file(open('/home/viren/apk/mfva_1.0.apk', 'rb'))

# Note the file just uploaded
In [7]: client.get_files(4)
Out[7]:
[File(id=6, name='MFVA', version='1.0', version_code='6'),
 File(id=7, name='MFVA', version='1.0', version_code='6')]

# Get analyses for the new file
In [8]: client.get_analyses(6)[:3]
Out[8]:
[Analysis(id=267, risk=2, status=3, cvss_base=6.8,
          findings=[{'title': None, 'description': 'Unprotected service: com.appknox.mfva.ExportedService'}],
          updated_on='2017-06-27 08:28:35.166608+00:00', vulnerability_id=1),
 Analysis(id=235, risk=3, status=3, cvss_base=7.3,
          findings=[{'title': None, 'description': 'pathPrefix=/'}],
          updated_on='2017-06-27 08:28:35.240543+00:00', vulnerability_id=2),
 Analysis(id=236, risk=3, status=3, cvss_base=7.7,
          findings=[{'title': None, 'description': 'Debug enabled within the app'}],
          updated_on='2017-06-27 08:28:35.296126+00:00', vulnerability_id=3)]

# Note the vulnerability_id for Analysis(id=235). To get details about the vulnerability
In [9]: client.get_vulnerability(2)
Out[9]: Vulnerability(name='Improper Content Provider Permissions',
                      description='A content provider permission was set to allow access from any other app on the device.
                                   Content providers may contain sensitive information about an app and therefore should not be shared.',
                      intro="The `ContentProvider` class provides a mechanism for managing and sharing data with other applications.
                             When sharing a provider's data with other apps, access control should be carefully implemented to prohibit unauthorized access to sensitive data.")
```

## Command-line interface

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
