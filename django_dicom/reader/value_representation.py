from enum import Enum

"""
This file contains an Enum with the two-character codes of the various DICOM value
representations for header elements.

*`One source`_*
*`Another source`_*

.. _One source: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
.. _Another source: http://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html

"""


class ValueRepresentation(Enum):
    """
    DICOM value representations.
    
    """

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
