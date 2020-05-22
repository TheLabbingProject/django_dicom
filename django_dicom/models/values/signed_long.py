from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_dicom.models.values.data_element_value import DataElementValue

MAX_VALUE = 2 ** 31 - 1
MIN_VALUE = -(2 ** 31)


class SignedLong(DataElementValue):
    value = models.IntegerField(
        validators=[MaxValueValidator(MAX_VALUE), MinValueValidator(MIN_VALUE)],
        blank=True,
        null=True,
    )
    raw = models.IntegerField(
        validators=[MaxValueValidator(MAX_VALUE), MinValueValidator(MIN_VALUE)],
        blank=True,
        null=True,
    )

