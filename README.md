# appknox-python
Python wrapper for Appknox's REST API

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
- [ ] Reports
    - [ ] PDF
    - [ ] JSON
    - [ ] XML
    - [ ] CSV
- [ ] Hooks
    - [ ] Create
    - [ ] Edit
    - [ ] Delete
