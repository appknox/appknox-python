.. appknox-python documentation master file, created by
   sphinx-quickstart on Tue Jun 27 17:07:07 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

appknox-python
###############

**Documentation for Version 3.x.x**

appknox-python provides command-line interface and Python wrapper for the
Appknox API.




Quickstart
----------

#. `Install`__
#. `Creating client instance`__
#. `Get organizations list`__
#. `Get projects list`__
#. `Get files list`__
#. `Get analysis list`__
#. `Get vulnerability details`__
#. `Upload app`__
#. `Recent Uploads`__
#. `Rescan`__
#. `Switch organization`__
#. `List Reports`__
#. `Create Report`__
#. `Get Report Summary CSV URL`__
#. `Get Report Summary Excel URL`__
#. `Download Report Data from URL`__
#. `Complete Reference`__

__

Install:
----------------------------
`appknox` is available via `PyPI <https://pypi.org/project/appknox/>`_. It is officially supported on python 3.5 & 3.6.

**Install with pip:**

.. code-block:: bash

    pip install appknox

__

Creating client instance:
----------------------------

Appknox class provides an easy access to the Appknox API.

Instances of this class can be used to interact with the Appknox scanner.

An instance for Appknox class can be obtained in two ways:

**1. Using personal access tokens:**
    .. code-block:: python

        import appknox
        client = appknox.Appknox(
            access_token='PERSONAL_ACCESS_TOKEN',
            host='API_HOST'
        )

    *Personal access token can be generated from Appknox dashboard
    (Settings → Developer Settings → Generate token)*

    .. note: Personal access token is the recommended way than using creadentials.

**2. Using login credentials: (This is not recommended)**

    .. code-block:: python

        import appknox
        client = appknox.Appknox(
            username='USERNAME',
            password='PASSWORD',
            host='API_HOST'
        )
        client.login(otp=013370)

    ``otp`` is required only for accounts with multi-factor authentication.

__

Get organizations list:
--------------------------

To list organizations for an authenticated user

.. code-block:: python

    client.get_organizations()

*Example:*

.. code-block:: python

    >>> client.get_organizations()
    [Organization(id=2, name='MyOrganization')]

All results are Python objects, with its respective attributes.

__

Get projects list:
---------------------

To list projects for which the authenticated user has access to in default organization.

.. code-block:: python

    client.get_projects()

*Example:*

.. code-block:: python

    >>> client.get_projects()
    [Project(id=3, created_on='2017-06-23 07:19:26.720829+00:00', file_count=3,
        package_name='org.owasp.goatdroid.fourgoats', platform=0,
        updated_on='2017-06-23 07:26:55.456744+00:00'),
    Project(id=4, created_on='2017-06-27 08:27:54.486226+00:00', file_count=1,
        package_name='com.appknox.mfva', platform=0,
        updated_on='2017-06-27 08:27:54.637432+00:00')]

All results are Python objects, with its respective attributes.

__

Get files list:
-------------------

For listing files within a project:

.. code-block:: python

    client.get_files(<project_id>)


*Example:*

.. code-block:: python

    >>> client.get_files(4)
    [File(id=6, name='MFVA', version='1.0', version_code='5', static_scan_progress=100),]

__

Get analysis list:
---------------------

Get the analyses for this new file:

.. code-block:: python

    client.get_analyses(<file_id>)

*Example:*

.. code-block:: python

>>> client.get_analyses(1405)[:2]
[
    Analysis(
        id=115449,
        risk=3,
        status=3,
        cvss_base=7.3,
        cvss_vector="CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L",
        cvss_version=3,
        cvss_metrics_humanized=[
            {"key": "Attack Vector", "value": "Local"},
            {"key": "Attack Complexity", "value": "Low"},
            {"key": "Privileges Required", "value": "Low"},
            {"key": "User Interaction", "value": "Not Required"},
            {"key": "Scope", "value": "Unchanged"},
            {"key": "Confidentiality Impact", "value": "High"},
            {"key": "Integrity Impact", "value": "High"},
            {"key": "Availability Impact", "value": "Low"},
        ],
        findings=[
            {
                "title": '<grant-uri-permission xmlns:android="http://schemas.android.com/apk/res/android" android:path="/" android:pathPrefix="/" android:pathPattern="*"/>',
                "description": "pathPrefix=/",
            }
        ],
        updated_on="2024-01-08T08:39:23.575462Z",
        vulnerability=2,
        owasp=["M1_2016"],
        pcidss=["3_2", "3_3", "3_4"],
        hipaa=["164_312_a_1"],
        cwe=["CWE_926"],
        mstg=["MSTG_6_1"],
        masvs=["MASVS_6_1"],
        asvs=[],
        gdpr=["gdpr_25", "gdpr_32"],
        nistsp80053=["RA_2", "RA_9", "AC_6", "SC_28", "AC_4", "AC_5", "PS_6", "AC_3"],
        nistsp800171=["3_1_1", "3_1_5", "3_13_16", "3_4_2"],
        computed_risk=3,
        overridden_risk=None,
    ),
]

Note the ``vulnerability_id`` for ``Analysis(id=235)``. To get details about this vulnerability:

__

Get vulnerability details:
-----------------------------

.. code-block:: python

    client.get_vulnerability(<vulnerability_id>)

*Example:*

.. code-block:: python

    >>> client.get_vulnerability(2)
    Vulnerability(name='Improper Content Provider Permissions',
        description='A content provider permission was set to allow access from any other app on the device.
            Content providers may contain sensitive information about an app and therefore should not be shared.',
        intro="The `ContentProvider` class provides a mechanism for managing and sharing data with other applications.
            When sharing a provider's data with other apps, access control should be carefully implemented to prohibit unauthorized access to sensitive data.")

__

Upload app:
-------------------

To upload and scan a new package:

.. code-block:: python

    >>> file_id = client.upload_file(<binary_data>)


*Example:*

.. code-block:: python

    >>> f = open('/home/username/apk/mfva_1.0.apk', 'rb')
    >>> file_data = f.read()
    >>> file_id = client.upload_file(file_data)
    >>> client.get_file(file_id)
    File(id=11469, name='MFVA', version='1.0', version_code='6', static_scan_progress=100)

__

Recent Uploads:
-------------------

Get recent file uploads by the user:

.. code-block:: python

    >>> client.recent_uploads()


*Example:*

.. code-block:: python

    >>> client.recent_uploads()
    [Submission(id=15506, status=7, file=11469, package_name='com.appknox.mfva', created_on='2019-05-06T16:04:50.094503Z', reason=''),
     Submission(id=15438, status=7, file=11405, package_name='com.appknox.mfva', created_on='2019-05-02T17:36:38.374191Z', reason=''),
     Submission(id=15437, status=7, file=11404, package_name='com.appknox.mfva', created_on='2019-05-02T17:35:29.245553Z', reason=''),
     Submission(id=15436, status=7, file=11403, package_name='com.appknox.mfva', created_on='2019-05-02T17:33:36.399803Z', reason=''),]

__

Rescan:
-------------------

To rescan a file:

.. code-block:: python

    >>> client.rescan(<file_id>)

This will create a new file under the same project. Once the file has been started, list files to get the latest file id.


*Example:*

.. code-block:: python

    >>> client.rescan(7)

    >>> client.get_files(4)
    [File(id=8, name='MFVA', version='1.0', version_code='6', static_scan_progress=100),
        File(id=7, name='MFVA', version='1.0', version_code='6', static_scan_progress=100),,
        File(id=6, name='MFVA', version='1.0', version_code='5', static_scan_progress=100),]

__

Switch organization:
----------------------------
Change default organization for client instance.

.. code-block:: python

    >>> client.switch_organization(<organization_id>)

*Example:*

.. code-block:: python

    >>> client.switch_organization(3)
    True

__

List Reports:
----------------------------
List all reports for a given File ID.

.. code-block:: python

    >>> client.list_reports(<file_id>)

*Example:*

.. code-block:: python

    >>> client.list_reports(95)
    [Report(id=105, language='en', generated_on='2023-01-24T06:37:05.565031Z', progress=100, rating='21.62', preferences=ReportPreference(show_api_scan=True, show_manual_scan=True, show_static_scan=True, show_dynamic_scan=True, show_ignored_analyses=False, show_hipaa=InheritedPreference(value=True, is_inherited=True), show_pcidss=InheritedPreference(value=True, is_inherited=True)))]

__

Create Report:
----------------------------
Creates a new report for given file ID

.. code-block:: python

    >>> client.create_report(<file_id>)

*Example:*

.. code-block:: python

    >>> client.create_report(94)
    Report(id=110, language='en', generated_on='2023-01-25T11:52:35.253614Z', progress=0, rating='6.76', preferences=ReportPreference(show_api_scan=True, show_manual_scan=True, show_static_scan=True, show_dynamic_scan=True, show_ignored_analyses=False, show_hipaa=InheritedPreference(value=True, is_inherited=True), show_pcidss=InheritedPreference(value=True, is_inherited=True)))

__

Get Report Summary CSV URL:
----------------------------
Returns a absolute URL to download report summary in CSV format for given report ID

.. code-block:: python

    >>> client.get_summary_csv_report_url(<report_id>)

*Example:*

.. code-block:: python

    >>> client.get_summary_csv_report_url(110)
    'https://api.appknox.com/api/v2/reports/110/summary_csv_download?sig=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InJhamFuIn0:1pKeRU:U4qF1EQ3QJDFRCf33nvcZiLzmI4jZNlcR4sDqAW2_IM:1pKeRU:70aBOcQY8-Lm75IT4E41wr7oRkyHabZX6a9lO_tdTZk'

__

Get Report Summary Excel URL
-----------------------------
Returns a absolute URL to download report summary in Excel format for given report ID

.. code-block:: python

    >>> client.get_summary_excel_report_url(<report_id>)

*Example:*

.. code-block:: python

    >>> client.get_summary_excel_report_url(110)
    'https://api.appknox.com/api/v2/reports/110/summary_excel_download?sig=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InJhamFuIn0:1pKeTf:skTH0btBf6IWT8TfBZYszT2ymXnT2CJRatKzf_kZwLE:1pKeTf:1Nf1z-lU6V7EMdtnBk0nKKcFH0clrdthBRa1DIbbVFU'

__

Download Report Data from URL
------------------------------
Returns full HTTP response body from a given absolute URL

.. code-block:: python

    >>> client.download_report_data(<url>)

*Examples:*

.. code-block:: python

    >>> client.download_report_data('https://api.appknox.com/api/v2/reports/110/summary_excel_download?sig=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InJhamFuIn0:1pKeTf:skTH0btBf6IWT8TfBZYszT2ymXnT2CJRatKzf_kZwLE:1pKeTf:1Nf1z-lU6V7EMdtnBk0nKKcFH0clrdthBRa1DIbbVFU')
    b'PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00?\x008\x9d\x86\xd8>\x01\x00\x00\x07\x04\x00\x00\x13\x00\x00\x00[Content_Types].xml\xad\x93\xcbn\xc3 \x10E\xf7\xfd\n\xc4\xb62$]TU\x15\'\x8b>\x96m\x16\xe9\x07P\x18\xc7(\x18\x103I\x93\xbf/\xb6\x93H\xad\xd2<\x94n\x8c\xcc\xdc...(Truncated)

.. code-block:: python

    >>> client.download_report_data('https://api.appknox.com/api/v2/reports/110/summary_csv_download?sig=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InJhamFuIn0:1pKeZL:Rr8IyficPV19ik0GYBX7caY-qCswKCOEecFYbuCuo_w:1pKeZL:D0i-AzRv5IuFy1MhGINuxCQW41zgHiuC1DKsgsfGG8Y')
    b'Project ID,Application Name,Application Namespace,Platform,Version,Version Code,File ID,Test Case,Scan Type,Severity,Risk Override,CVSS Score,Findings,Description,Noncompliant Code Example,Compliant Solution,Business Implication,OWASP...(Truncated)

__

Complete Reference
-------------------

.. toctree::
   :maxdepth: 2

   client

   mapper

--

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
