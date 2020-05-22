from django.db import models
from django.core.validators import MaxValueValidator
from django_dicom.models.values.data_element_value import DataElementValue

MAX_VALUE = 2 ** 32


class UnsignedLong(DataElementValue):
    value = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_VALUE)], blank=True, null=True
    )
    raw = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_VALUE)], blank=True, null=True
    )

