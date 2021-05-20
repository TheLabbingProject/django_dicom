"""
Definition of the :class:`FloatingPointDouble` model.
"""
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class FloatingPointDouble(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single
    *FloatingPointDouble* data element value.
    """

    value = models.FloatField(blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign a :class:`~django.db.models.FloatField`.
    """

    raw = models.CharField(max_length=64, blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign a :class:`~django.db.models.CharField`.
    """
