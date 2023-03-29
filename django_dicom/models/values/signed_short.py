"""Definition of the :class:`SignedShort` model."""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_dicom.models.values.data_element_value import DataElementValue

#: Minimal *SignedShort* value.
MIN_VALUE = -(2 ** 15)
#: Maximal *SignedShort* value.
MAX_VALUE = 2 ** 15 - 1


class SignedShort(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *SignedShort*
    data element value.
    """

    value = models.IntegerField(
        validators=[MaxValueValidator(MAX_VALUE), MinValueValidator(MIN_VALUE)],
        blank=True,
        null=True,
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    to assign an :class:`~django.db.models.IntegerField`.
    """

    raw = models.IntegerField(
        validators=[MaxValueValidator(MAX_VALUE), MinValueValidator(MIN_VALUE)],
        blank=True,
        null=True,
    )
    """
    Overrides
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    to assign an :class:`~django.db.models.IntegerField`.
    """
