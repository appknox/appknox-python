[![Build Status](https://travis-ci.org/appknox/appknox-python.svg)](https://travis-ci.org/appknox/appknox-python)
[![Join the chat at https://gitter.im/appknox/appknox-python](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/appknox/appknox-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Stories in Ready](https://badge.waffle.io/appknox/appknox-python.png?label=ready&title=Ready)](https://waffle.io/appknox/appknox-python)

# appknox-python

CLI tool & Python wrapper for Appknox API

## Installation
```
[sudo] pip install appknox
```

## Usage

### Authentication

#### Method 1

Specify credentials in environment with variables `APPKNOX_USERNAME` and `APPKNOX_PASSWORD`
```
export APPKNOX_USERNAME="YourUseranme"
export APPKNOX_PASSWORD="YourPassword"
```

To check if it is properly configured, run `appknox validate`

#### Method 2

You can also pass it as options

```
appknox --username YourUseranme --password YourPassword validate
```

Method 1 is recommended because it is cleaner. From this point forward, the documentation will give examples assuming you have used Method 1. You just have to pass `--username` and `--password` for `appknox` if you opt for method 2.

### Submit app by store URL

```
appknox submit_url "<Your store URL Goes here>"
```

### Submit app by file

```
appknox upload /path/to/your/android.apk
appknox upload /path/to/your/ios.ipa
```

### Help
```
$ appknox --help

Usage: appknox [OPTIONS] COMMAND [ARGS]...

  Command line wrapper for the Appknox API

Options:
  --username TEXT  Username
  --password TEXT  Password
  --level INTEGER  Log level
  --host TEXT      API host
  --help           Show this message and exit.

Commands:
  analyses_list    Get analyses by file ID
  dynamic_restart  Restart dynamic scan for file
  dynamic_start    Start dynamic scan for file
  dynamic_stop     Stop dynamic scan for file
  file_get         Get file by ID
  file_list        Get list of files for a project with ID
  payment          Make payment
  project_get      Get project by ID
  project_list     Get list of projects
  report           Get report with format_type and file_id
  submit_url       Submit app by store URL
  upload           Submit app by uploading file
  validate         Validate if credentials are correct
  vulnerability    Get report with format_type and file_id
```

## Todo

- [x] Authentication
- [x] Authorization
- [ ] Versioning
- [x] Submit URL
- [x] Upload File
- [x] Projects
    - [x] List
    - [x] Get
    - [ ] ~~Delete~~ (depricated/removed)
- [x] Files
    - [x] List
    - [x] Get
    - [ ] ~~Delete~~ (depricated/removed)
- [x] Analyses
    - [x] List
- [x] Reports
    - [x] PDF
    - [x] JSON
    - [x] XML
    - [x] CSV
- [ ] Hooks
    - [ ] Create
    - [ ] Edit
    - [ ] Delete

---

License: MIT
