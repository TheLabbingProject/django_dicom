from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class ShortText(DataElementValue):
    value = models.CharField(max_length=1024, blank=True, null=True)
    raw = models.CharField(max_length=1024, blank=True, null=True)
