from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.models.validators import digits_and_dots_only


class UniqueIdentifier(DataElementValue):
    value = models.CharField(
        max_length=64, validators=[digits_and_dots_only], blank=True, null=True,
    )
    raw = models.CharField(max_length=64, blank=True, null=True)
