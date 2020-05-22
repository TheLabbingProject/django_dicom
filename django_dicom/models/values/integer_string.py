from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue

MAX_VALUE = 2 ** 31 - 1
MIN_VALUE = -(2 ** 31)


class IntegerString(DataElementValue):
    value = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE), MaxValueValidator(MAX_VALUE)],
        blank=True,
        null=True,
    )
    raw = models.CharField(max_length=12, blank=True, null=True)
