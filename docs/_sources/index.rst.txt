.. appknox-python documentation master file, created by
   sphinx-quickstart on Tue Jun 27 17:07:07 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

appknox-python
==========================================

appknox-python provides command-line interface and Python wrapper for the
Appknox API.

Contents
--------

.. toctree::
   :maxdepth: 2

   client
   mapper


Quickstart
----------

    Appknox class provides an easy access to the Appknox API.

    Instances of this class can be used to interact with the Appknox scanner.

    To obtain an instance of this class:

    .. code-block:: python

        In[1]: import appknox
        In[2]: appknox = appknox.Appknox(
                                username='USERNAME',
                                password='PASSWORD',
                                host='HOST')

    To perform authentication:

    .. code-block:: python

        In[3]: appknox.login(otp=013370)

    ``otp`` is required only for accounts with multi-factor authentication.

    To list projects for authenticated user

    .. code-block:: python

        In [4]: client.get_projects()
        Out[4]:
        [Project(id=3, created_on='2017-06-23 07:19:26.720829+00:00', file_count=3,
                 package_name='org.owasp.goatdroid.fourgoats', platform=0,
                 updated_on='2017-06-23 07:26:55.456744+00:00'),
         Project(id=4, created_on='2017-06-27 08:27:54.486226+00:00', file_count=1,
                 package_name='com.appknox.mfva', platform=0,
                 updated_on='2017-06-27 08:27:54.637432+00:00')]

    All results are Python objects, with its respective attributes.

    For listing files within a project:

    .. code-block:: python

        In [5]: client.get_files(4)
        Out[5]: [File(id=6, name='MFVA', version='1.0', version_code='6')]

    To upload and scan a new package:

    .. code-block:: python

        In [6]: client.upload_file(open('/home/viren/apk/mfva_1.0.apk', 'rb'))

    Note the file that was just uploaded below:

    .. code-block:: python

        In [7]: client.get_files(4)
        Out[7]:
        [File(id=6, name='MFVA', version='1.0', version_code='6'),
         File(id=7, name='MFVA', version='1.0', version_code='6')]

    Get the analyses for this new file:

    .. code-block:: python

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

    Note the ``vulnerability_id`` for ``Analysis(id=235)``. To get details about this vulnerability:

    .. code-block:: python

        In [9]: client.get_vulnerability(2)
        Out[9]: Vulnerability(name='Improper Content Provider Permissions',
                              description='A content provider permission was set to allow access from any other app on the device.
                                           Content providers may contain sensitive information about an app and therefore should not be shared.',
                              intro="The `ContentProvider` class provides a mechanism for managing and sharing data with other applications.
                                     When sharing a provider's data with other apps, access control should be carefully implemented to prohibit unauthorized access to sensitive data.")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
