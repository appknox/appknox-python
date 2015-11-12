[![Build Status](https://travis-ci.org/appknox/appknox-python.svg)](https://travis-ci.org/appknox/appknox-python)
[![Stories in Ready](https://badge.waffle.io/appknox/appknox-python.png?label=ready&title=Ready)](https://waffle.io/appknox/appknox-python)
[![Join the chat at https://gitter.im/appknox/appknox-python](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/appknox/appknox-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
# appknox-python

CLI tool & Python wrapper for Appknox's REST API

## Installation
```
[sudo] pip install appknox
```

## Usage

### Credentials
***Method 1***

You can either specify credentials in your `ENV` variables `APPKNOX_USERNAME` & `APPKNOX_PASSWORD`
```
export APPKNOX_USERNAME="YourUseranme"
export APPKNOX_PASSWORD="YourPassword"
```
to check if it is properly configured, just do `appknox validate`

***Method 2***

You can aslo pass it as an option.

`appknox --username YourUseranme --password YourPassword validate`

Method-1 is recommended because its more clean. From this point forward, the documentation will give examples assuming you have used Method-1. You just have to pass `--username` and `--password` for `appknox` if you opt for method-2.

### Submit a store URL

```
appknox submit_url "<Your store URL Goes here>"
```

### Uploading your App

```
appknox upload /path/to/your/android.apk
appknox upload /path/to/your/ios.ipa
```

### Help
```
appknox --help
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
    - [ ] Delete
- [x] Files
    - [x] List
    - [x] Get
    - [ ] Delete
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
