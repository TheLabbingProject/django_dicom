"""
Creates :class:`~django.db.models.Model` subclasses to represent the various
DICOM entities.

"""

from django_dicom.models.header import Header
from django_dicom.models.image import Image
from django_dicom.models.series import Series
from django_dicom.models.patient import Patient
from django_dicom.models.study import Study
from django_dicom.models.data_element import DataElement
from django_dicom.models.data_element_definition import DataElementDefinition
