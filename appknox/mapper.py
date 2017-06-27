# (c) 2017, XYSec Labs

from collections import namedtuple


def mapper(model: type, resource: dict) -> object:
    """
    Returns an object of type 'model' from dictified JSON 'resource'

    :param model:
    :param resource:
    :type model: type
    :type resource: dict
    :return:
    :rtype: object
    """
    attr = dict()
    for field in model._fields:
        if field == 'id':
            attr[field] = resource['data']['id']
        else:
            attr[field] = resource['data']['attributes'].get(
                field.replace('_', '-'), None)
    return model(**attr)


User = namedtuple(
    'User',
    ['id', 'email', 'first_name', 'lang', 'last_name', 'username']
)

Project = namedtuple(
    'Project',
    ['id', 'created_on', 'file_count', 'package_name', 'platform',
     'updated_on']
)

File = namedtuple(
    'File',
    ['id', 'name', 'version', 'version_code']
)

Analysis = namedtuple(
    'Analysis',
    ['id', 'risk', 'status', 'cvss_base', 'findings', 'updated_on',
     'vulnerability_id']
)

Vulnerability = namedtuple(
    'Vulnerability',
    ['name', 'description', 'intro', 'compliant', 'non_compliant']
)
