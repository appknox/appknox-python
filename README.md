[![PyPI version](https://badge.fury.io/py/appknox.svg)](https://badge.fury.io/py/appknox)
[![Build Status](https://travis-ci.org/appknox/appknox-python.svg)](https://travis-ci.org/appknox/appknox-python)
[![Join the chat at https://gitter.im/appknox/appknox-python](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/appknox/appknox-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# appknox-python

Command-line interface & Python wrapper for the Appknox API.


>
> Python API documentation is available [here](http://appknox.org/appknox-python/).
>


## Installation

appknox-python is officially supported on python 3.5 & 3.6. pip is the recommended way to install appknox-python.

```
pip install appknox
```

## Usage

```
$ appknox
Usage: appknox [OPTIONS] COMMAND [ARGS]...

  Command line wrapper for the Appknox API

Options:
  -v, --verbose  Specify log verbosity.
  -k, --insecure      Allow Insecure Connection
  --help         Show this message and exit.

Commands:
  analyses       List analyses for file
  files          List files for project
  login          Log in and save session credentials
  logout         Delete session credentials
  organizations  List organizations
  projects       List projects
  recent_uploads List recent file uploads by the user
  report         Download report for file
  upload         Upload and scan package
  switch_organization  Switch organization in CLI instance
  vulnerability  Get vulnerability
  whoami         Show session info
```

### Authentication

Log in to appknox CLI using your [secure.appknox.com](https://secure.appknox.com/) credentials.

```
$ appknox login
Username: viren
Password:
Logged in to https://api.appknox.com
```

#### Using Environment Variables

Instead of `login` we can use environment variables for authentication. This will be useful for scenarios such as CI/CD setup.

```
$ export APPKNOX_ACCESS_TOKEN=aaaabbbbbcccddeeeffgghhh
$ export APPKNOX_ORGANIZATION_ID=2
$ export HTTP_PROXY=http://proxy.local
$ export HTTPS_PROXY=https://proxy.local
```

Supported variables are:

| Environment variable | Value |
|----|-----|
| `APPKNOX_ACCESS_TOKEN` | Access token can be generated from Appknox dashboard _(Settings → Developer Settings → Generate token)_. |
| `APPKNOX_HOST` | Defaults to `https://api.appknox.com` |
| `APPKNOX_ORGANIZATION_ID` | Your Appknox organization id |
| `HTTP_PROXY` | Set your HTTP proxy ex: `http://proxy.local` |
| `HTTPS_PROXY` | Set your HTTPS proxy ex: `https://proxy.local` |


### Data fetch & actions

| Available commands | Use |
|--------------------|-----|
| `organizations` | List organizations of user |
| `projects` | List projects user has access to |
| `files <project_id>` | List files for a project |
| `analyses <file_id>` | List analyses for a file |
| `vulnerability <vulnerability_id>` | Get vulnerability detail |
| `owasp <owasp_id>` | Get OWASP detail |
| `upload <path_to_app_package>` | Upload app file from given path and get the file_id |
| `rescan <file_id>` | Rescan a file (this will create a new file under the same project.) |


Example:

```
$ appknox organizations
  id  name
----  -------
   2  MyOrganization

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

### Using Proxy

Appknox client and CLI both supports HTTP and HTTPS proxy. While using the client, if you need to set-up a proxy then please follow the example below

```
from appknox.client import Appknox

client = Appknox(
        access_token="<Your Access Token",  #  This is your access token which you can get from developer setting
        https_proxy="http://proxy.local",   # Use https_proxy by default since cloud server connects to https service
        insecure=True,                      # Use insecure connections, because proxies might have their own set of certificates which maynot be trusted
    )                                       # Insecure connections are not reccomended though
```

To use it in CLI example:

```
$ export HTTPS_PROXY=http://127.0.0.1:8080 
$ appknox --insecure login
Username:
```

*Note*: Please avoid using `--insecure` flag or setting `insecure=True` in client, this will allow an attacker to perform MITM attack, but this might be required for proxies to work alongside.

---

## Development
### Update docs

Install [sphinx-autobuild](https://github.com/GaretJax/sphinx-autobuild):
```
pip install sphinx-autobuild
```

Build docs:
```
sphinx-autobuild -b html sphinx-docs docs
```

---

License: MIT
