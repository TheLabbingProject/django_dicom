from dicom_parser.utils.value_representation import ValueRepresentation
from django.conf import settings

IMPORT_MODES = {
    "minimal": {"tags": [], "vrs": [ValueRepresentation.SQ]},
    "normal": {"tags": [], "vrs": []},
    "full": {"tags": [], "vrs": []}
}

def field_validator(self, data_element) -> bool:
    tags = settings.FIELDS_TO_EXCLUDE["tags"]
    vrs = settings.FIELDS_TO_EXCLUDE["vrs"]
    for tag in tags:
        if data_element.tag == tag:
            return False
    for vr in vrs:
        if data_element.VALUE_REPRESENTATION == vr:
            return False
    return True