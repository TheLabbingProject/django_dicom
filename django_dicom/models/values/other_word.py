"""
Definition of the :class:`OtherWord` model.
"""
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class OtherWord(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *OtherWord*
    data element value.
    """

    value = ArrayField(models.IntegerField(), blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign a :class:`~django.db.models.IntegerField`.
    """

    raw = models.BinaryField(blank=True, null=True)
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign a :class:`~django.db.models.BinaryField`.
    """
