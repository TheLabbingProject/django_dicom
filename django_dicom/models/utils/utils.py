from dicom_parser.utils.value_representation import ValueRepresentation
from django.conf import settings
from enum import Enum


class ImportMode(Enum):
    MINIMAL = "Minimal"
    NORMAL = "Normal"
    FULL = "Full"


PIXEL_ARRAY_TAG = "7fe0", "0010"

IMPORT_MODE_CONFIGURATION = {
    ImportMode.MINIMAL: {"tags": [], "vrs": [ValueRepresentation.SQ]},
    ImportMode.NORMAL: {"tags": [], "vrs": [ValueRepresentation.SQ]},
    ImportMode.FULL: {"tags": [], "vrs": []},
}


def get_import_configuration() -> dict:
    try:
        definition = settings.DICOM_IMPORT_MODE
        import_mode = ImportMode[definition.upper()]
    except AttributeError:
        import_mode = ImportMode.NORMAL
    return IMPORT_MODE_CONFIGURATION.get(import_mode, ImportMode.NORMAL)


def check_element_inclusion(data_element) -> bool:
    import_configuration = get_import_configuration()
    tags = import_configuration["tags"]
    vrs = import_configuration["vrs"]
    excluded_tag = any([data_element.tag in (tag, PIXEL_ARRAY_TAG) for tag in tags])
    excluded_vr = any([vr == data_element.VALUE_REPRESENTATION for vr in vrs])
    return not (excluded_tag or excluded_vr)


def snake_case_to_camel_case(string: str) -> str:
    return "".join([part.title() for part in string.split("_")])
