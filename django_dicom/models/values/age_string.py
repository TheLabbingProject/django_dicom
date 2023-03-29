"""
Definition of the :class:`AgeString` model.
"""
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class AgeString(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *AgeString* data
    element value.
    """

    value = models.FloatField(verbose_name="Age in years", blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign a :class:`~django.db.models.FloatField`.
    """

    raw = models.CharField(max_length=4, blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign a :class:`~django.db.models.CharField`.
    """
