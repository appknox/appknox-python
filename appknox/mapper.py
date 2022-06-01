# (c) 2017, XYSec Labs

from collections import namedtuple
from dataclasses import dataclass

def mapper_json_api(model: type, resource: dict) -> object:
    """
    Returns an obj of type `model` from dictified JSON `resource` for JSON APIs
    """
    attr = dict()
    for field in model._fields:
        if field == 'id':
            attr[field] = resource['data']['id']
        else:
            attr[field] = resource['data']['attributes'][
                field.replace('_', '-')]
    return model(**attr)


def mapper_drf_api(model: type, resource: dict) -> object:
    """
    Returns an obj of type `model` from dictified JSON `resource` for DRF APIs
    """
    accepted_params = {k: resource[k] for k in model._fields}
    return model(**accepted_params)


User = namedtuple(
    'User',
    ['id', 'email', 'first_name', 'lang', 'last_name', 'username']
)

Whoami = namedtuple(
    'Whoami',
    ['id', 'email', 'username', 'default_organization']
)

Organization = namedtuple(
    'Organization',
    ['id', 'name']
)

Project = namedtuple(
    'Project',
    ['id', 'created_on', 'file_count', 'package_name', 'platform',
     'updated_on']
)

File = namedtuple(
    'File',
    ['id', 'name', 'version', 'version_code', 'static_scan_progress', 'profile']
)

Submission = namedtuple(
    'Submission',
    ['id', 'status', 'file', 'package_name', 'created_on', 'reason']
)

Analysis = namedtuple(
    'Analysis',
    ['id', 'risk', 'status', 'cvss_base', 'cvss_vector', 'cvss_version',
     'cvss_metrics_humanized', 'findings', 'updated_on', 'vulnerability',
     'owasp', 'pcidss', 'hipaa', 'cwe', 'mstg', 'asvs', 'gdpr', 'computed_risk', 'overridden_risk']
)

Vulnerability = namedtuple(
    'Vulnerability',
    ['id', 'name', 'description', 'intro', 'related_to',
     'business_implication', 'compliant', 'non_compliant', 'types']
)

OWASP = namedtuple(
    'OWASP',
    ['id', 'code', 'title', 'description', 'year']
)

PCIDSS = namedtuple(
    'PCIDSS',
    ['id', 'code', 'title', 'description']
)

PersonalToken = namedtuple(
    'AccessToken',
    ['name', 'key']
)

ReportPreferenceMapper = {
    'show_pcidss': 'pcidss',
    'show_hipaa': 'hipaa',
    'show_gdpr': 'gdpr'}

@dataclass
class ProfileReportPreferenceConfig:
    value: bool

@dataclass
class ProfileReportPreference:
    show_gdpr: ProfileReportPreferenceConfig
    show_hipaa: ProfileReportPreferenceConfig
    show_pcidss: ProfileReportPreferenceConfig

    @classmethod
    def from_json(cls, data):
        return cls(
            show_gdpr=ProfileReportPreferenceConfig(value=data['show_gdpr']['value']),
            show_hipaa=ProfileReportPreferenceConfig(value=data['show_hipaa']['value']),
            show_pcidss=ProfileReportPreferenceConfig(value=data['show_pcidss']['value'])
        )
