from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class FloatingPointSingle(DataElementValue):
    value = models.FloatField(blank=True, null=True)
    raw = models.CharField(max_length=32, blank=True, null=True)
