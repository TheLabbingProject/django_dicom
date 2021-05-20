"""
Definition of the :class:`DateTime` model.
"""
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class DateTime(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *DateTime* data
    element value.
    """

    value = models.DateTimeField()
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign a :class:`~django.db.models.CharField`.
    """

    raw = models.CharField(
        max_length=26, help_text="YYYYMMDDHHMMSS.FFFFFF&ZZXX"
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign a :class:`~django.db.models.CharField`.
    """
