import array
import pydicom

from datetime import datetime
from enum import Enum

"""
Source:
http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
"""


class ValueRepresentation(Enum):
    APPLICATION_ENTITY = "AE"
    AGE_STRING = "AS"
    ATTRIBUTE_TAG = "AT"
    CODE_STRING = "CS"
    DATE = "DA"
    DECIMAL_STRING = "DS"
    DATE_TIME = "DT"
    FLOATING_POINT_SINGLE = "FL"
    FLOATING_POINT_DOUBLE = "FD"
    INTEGER_STRING = "IS"
    LONG_STRING = "LO"
    LONG_TEXT = "LT"
    OTHER_BYTE = "OB"
    OTHER_DOUBLE = "OD"
    OTHER_FLOAT = "OF"
    OTHER_LONG = "OL"
    OTHER_64_BIT_VERY_LONG = "OV"
    OTHER_WORD = "OW"
    PERSON_NAME = "PN"
    SHORT_STRING = "SH"
    SIGNED_LONG = "SL"
    SEQUENCE_OF_ITEMS = "SQ"
    SIGNED_SHORT = "SS"
    SHORT_TEXT = "ST"
    SIGNED_64_BIT_VERY_LONG = "SV"
    TIME = "TM"
    UNLIMITED_CHARACTERS = "UC"
    UNIQUE_IDENTIFIER = "UI"
    UNSIGNED_LONG = "UL"
    UNKNOWN = "UN"
    UNIVERSAL_RESOURCE = "UR"
    UNSIGNED_SHORT = "US"
    UNLIMITED_TEXT = "UT"
    UNSIGNED_64_BIT_VERY_LONG = "UV"


class Sex(Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


N_IN_YEAR = {"Y": 1, "M": 12, "W": 52.1429, "D": 365.2422}


def parse_age_string(element: pydicom.dataelem.DataElement) -> float:
    value = element.value
    duration, units = float(value[:-1]), value[-1]
    return duration / N_IN_YEAR[units]


def parse_date(element: pydicom.dataelem.DataElement) -> datetime.date:
    return datetime.strptime(element.value, "%Y%m%d").date()


def parse_decimal_string(element: pydicom.dataelem.DataElement):
    return float(element.value)


def parse_time(element: pydicom.dataelem.DataElement) -> datetime.time:
    return datetime.strptime(element.value, "%H%M%S.%f").time()


def parse_datetime(element: pydicom.dataelem.DataElement) -> datetime:
    return datetime.strptime(element.value, "%Y%m%d%H%M%S.%f")


def parse_slice_timing(value: bytes) -> list:
    return [round(slice_time, 5) for slice_time in list(array.array("d", value))]


def parse_gradient_direction(value: bytes) -> list:
    return [float(value) for value in list(array.array("d", value))]


def parse_unknown(element: pydicom.dataelem.DataElement):
    # Siemens DWI tags
    # https://na-mic.org/wiki/NAMIC_Wiki:DTI:DICOM_for_DWI_and_DTI
    # Number of Images in Mosaic
    if element.tag == ("0019", "100a"):
        return int.from_bytes(element.value, byteorder="little")
    # Slice Measurement Duration
    elif element.tag == ("0019", "100b"):
        return float(element.value)
    # B Value
    elif element.tag == ("0019", "100c"):
        return int(element.value)
    # Diffusion Directionality / Gradient Mode
    elif element.tag in [("0019", "100d"), ("0019", "100f")]:
        return element.value.decode("utf-8").strip()
    # Diffusion Gradient Direction
    elif element.tag == ("0019", "100e"):
        return parse_gradient_direction(element.value)
    # B Matrix
    elif element.tag == ("0019", "1027"):
        return list(array.array("d", element.value))
    # Bandwidth per Pixel Phase Encode
    elif element.tag == ("0019", "1028"):
        return array.array("d", element.value)[0]

    # Siemens slice timing
    elif element.tag == ("0019", "1029"):
        return parse_slice_timing(element.value)
    return None


def parse_code_string(element: pydicom.dataelem.DataElement) -> str:
    # Patient Sex
    if element.tag == ("0010", "0040"):
        return Sex(element.value).name.title()


PARSER_DICT = {
    ValueRepresentation.AGE_STRING: parse_age_string,
    ValueRepresentation.DATE: parse_date,
    ValueRepresentation.TIME: parse_time,
    ValueRepresentation.DATE_TIME: parse_datetime,
    ValueRepresentation.INTEGER_STRING: int,
    ValueRepresentation.SEQUENCE_OF_ITEMS: list,
    ValueRepresentation.UNKNOWN: parse_unknown,
    ValueRepresentation.CODE_STRING: parse_code_string,
}


def parse_element(element: pydicom.dataelem.DataElement):
    try:
        value_representation = ValueRepresentation(element.VR)
        try:
            return PARSER_DICT[value_representation](element)
        except KeyError:
            return element.value
    except AttributeError:
        return None
