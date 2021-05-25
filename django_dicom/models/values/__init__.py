"""
Definition of
:class:`~django_dicom.models.values.data_element_value.DataElementValue`
subclasses for every type of value representation (VR).

Hint
----
For more information about value representations see the `official DICOM
standard`_ (`part 05, section 6.2`_).

.. _official DICOM standard: https://www.dicomstandard.org/current/
.. _part 05, section 6.2:
   http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
"""
from django_dicom.models.values.age_string import AgeString
from django_dicom.models.values.application_entity import ApplicationEntity
from django_dicom.models.values.code_string import CodeString
from django_dicom.models.values.csa_header import CsaHeader
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.models.values.date import Date
from django_dicom.models.values.datetime import DateTime
from django_dicom.models.values.decimal_string import DecimalString
from django_dicom.models.values.floating_point_double import (
    FloatingPointDouble,
)
from django_dicom.models.values.floating_point_single import (
    FloatingPointSingle,
)
from django_dicom.models.values.integer_string import IntegerString
from django_dicom.models.values.long_string import LongString
from django_dicom.models.values.long_text import LongText
from django_dicom.models.values.other_word import OtherWord
from django_dicom.models.values.person_name import PersonName
from django_dicom.models.values.sequence_of_items import SequenceOfItems
from django_dicom.models.values.short_string import ShortString
from django_dicom.models.values.short_text import ShortText
from django_dicom.models.values.signed_long import SignedLong
from django_dicom.models.values.signed_short import SignedShort
from django_dicom.models.values.time import Time
from django_dicom.models.values.unique_identifier import UniqueIdentifier
from django_dicom.models.values.unknown import Unknown
from django_dicom.models.values.unlimited_text import UnlimitedText
from django_dicom.models.values.unsigned_long import UnsignedLong
from django_dicom.models.values.unsigned_short import UnsignedShort

# flake8: noqa: F401
