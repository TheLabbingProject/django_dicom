"""
Definition of the :class:`UnsignedLong` model.
"""
from django.core.validators import MaxValueValidator
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue

#: Maximal *UnsignedLong* value.
MAX_VALUE = 2 ** 32


class UnsignedLong(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *UnsignedLong*
    data element value.
    """

    value = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_VALUE)], blank=True, null=True
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign a :class:`~django.db.models.PositiveIntegerField`.
    """

    raw = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_VALUE)], blank=True, null=True
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign a :class:`~django.db.models.PositiveIntegerField`.
    """
