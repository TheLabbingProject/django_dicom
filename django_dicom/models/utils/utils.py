from enum import Enum
from pathlib import Path

from dicom_parser.utils.value_representation import ValueRepresentation
from django.apps import apps
from django.conf import settings


# Import Management
###################
class ImportMode(Enum):
    MINIMAL = "Minimal"
    NORMAL = "Normal"
    FULL = "Full"


DEFAULT_IMPORT_MODE: str = "MINIMAL"

PIXEL_ARRAY_TAG = "7fe0", "0010"

IMPORT_CONFIGURATIONS = {
    ImportMode.MINIMAL: None,
    ImportMode.NORMAL: {
        "tags": [
            # Siemens private tags
            ("0019", "0010"),
            ("0029", "0010"),
            ("0029", "0011"),
            ("0029", "0012"),
            ("0051", "0010"),
            ("7fe1," "0010"),
            # General Electric (GE) private tags
            ("0009", "0010"),
            ("0011", "0010"),
            ("0021", "0010"),
            ("0023", "0010"),
            ("0025", "0010"),
            ("0027", "0010"),
            ("0043", "0010"),
            # General
            ("0008", "0000"),
        ],
        "vrs": [ValueRepresentation.SQ, ValueRepresentation.UN],
    },
    ImportMode.FULL: {"tags": [], "vrs": []},
}


def get_import_mode() -> ImportMode:
    setting = getattr(settings, "DICOM_IMPORT_MODE", DEFAULT_IMPORT_MODE)
    try:
        return ImportMode[setting.upper()]
    except KeyError:
        return ImportMode[DEFAULT_IMPORT_MODE]


def get_import_configuration() -> dict:
    import_mode = get_import_mode()
    default = IMPORT_CONFIGURATIONS[ImportMode.NORMAL]
    return IMPORT_CONFIGURATIONS.get(import_mode, default)


def check_element_inclusion(data_element) -> bool:
    import_configuration = get_import_configuration()
    if import_configuration is None:
        return False
    tags = import_configuration["tags"]
    vrs = import_configuration["vrs"]
    excluded_tag = any(
        [data_element.tag in (tag, PIXEL_ARRAY_TAG) for tag in tags]
    )
    excluded_vr = any([vr == data_element.VALUE_REPRESENTATION for vr in vrs])
    return not (excluded_tag or excluded_vr)


# Media directory locations
###########################
DEFAULT_DICOM_DIR_NAME = "DICOM"
DEFAULT_MRI_DIR_NAME = "MRI"


def get_subject_model():
    app_label, model_name = settings.SUBJECT_MODEL.split(".")
    return apps.get_model(app_label=app_label, model_name=model_name)


def get_group_model():
    app_label, model_name = settings.STUDY_GROUP_MODEL.split(".")
    return apps.get_model(app_label=app_label, model_name=model_name)


def get_mri_root() -> Path:
    default = Path(settings.MEDIA_ROOT, DEFAULT_MRI_DIR_NAME)
    path = getattr(settings, "MRI_ROOT", default)
    return Path(path)


def get_dicom_root() -> Path:
    return get_mri_root() / DEFAULT_DICOM_DIR_NAME


# Other
#######
def snake_case_to_camel_case(string: str) -> str:
    return "".join([part.title() for part in string.split("_")])
