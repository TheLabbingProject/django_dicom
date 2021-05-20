"""
Definition of the :class:`SignedLong` model.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue

#: Minimal *SignedLong* value.
MIN_VALUE = -(2 ** 31)
#: Maximal *SignedLong* value.
MAX_VALUE = 2 ** 31 - 1


class SignedLong(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *SignedLong*
    data element value.
    """

    value = models.IntegerField(
        validators=[
            MaxValueValidator(MAX_VALUE),
            MinValueValidator(MIN_VALUE),
        ],
        blank=True,
        null=True,
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign an :class:`~django.db.models.IntegerField`.
    """

    raw = models.IntegerField(
        validators=[
            MaxValueValidator(MAX_VALUE),
            MinValueValidator(MIN_VALUE),
        ],
        blank=True,
        null=True,
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign an :class:`~django.db.models.IntegerField`.
    """
