"""
Definition of the :class:`Date` model.
"""
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class Date(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *Date* data
    element value.
    """

    value = models.DateField(blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign a :class:`~django.db.models.CharField`.
    """

    raw = models.CharField(max_length=8, help_text="YYYYMMDD", blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign a :class:`~django.db.models.CharField`.
    """
