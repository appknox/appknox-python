# (c) 2017, XYSec Labs

from collections import namedtuple


def mapper(model: type, resource: dict) -> object:
    """
    Returns an object of type `model` from dictified JSON `resource`
    """
    attr = dict()
    for field in model._fields:
        if field == 'id':
            attr[field] = resource['data']['id']
        else:
            attr[field] = resource['data']['attributes'][
                field.replace('_', '-')]
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
    ['id', 'name', 'version', 'version_code', 'static_scan_progress']
)

Analysis = namedtuple(
    'Analysis',
    ['id', 'risk', 'status', 'cvss_base', 'cvss_vector', 'cvss_version',
     'cvss_metrics_humanized', 'findings', 'updated_on', 'vulnerability_id']
)

Vulnerability = namedtuple(
    'Vulnerability',
    ['name', 'description', 'intro', 'related_to',
     'business_implication', 'compliant', 'non_compliant', 'types']
)

PersonalToken = namedtuple(
    'AccessToken',
    ['name', 'key']
)
