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
#. `Rescan`__
#. `Switch organization`__
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

    >>> client.get_analyses(6)[:3]
    [Analysis(id=267, risk=2, status=3, cvss_base=6.8,
        findings=[{'title': None, 'description': 'Unprotected service: com.appknox.mfva.ExportedService'}],
        updated_on='2017-06-27 08:28:35.166608+00:00', vulnerability_id=1),
    Analysis(id=235, risk=3, status=3, cvss_base=7.3,
        findings=[{'title': None, 'description': 'pathPrefix=/'}],
        updated_on='2017-06-27 08:28:35.240543+00:00', vulnerability_id=2),
    Analysis(id=236, risk=3, status=3, cvss_base=7.7,
        findings=[{'title': None, 'description': 'Debug enabled within the app'}],
        updated_on='2017-06-27 08:28:35.296126+00:00', vulnerability_id=3)]

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

    >>> client.upload_file(<binary_data>)


*Example:*

.. code-block:: python

    >>> f = open('/home/username/apk/mfva_1.0.apk', 'rb')
    >>> file_data = f.read()
    >>> client.upload_file(file_data)

    >>> client.get_files(4)
    [File(id=7, name='MFVA', version='1.0', version_code='6', static_scan_progress=100),,
        File(id=6, name='MFVA', version='1.0', version_code='5', static_scan_progress=100),]

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
