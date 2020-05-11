from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class LongText(DataElementValue):
    value = models.TextField(blank=True, null=True)
    raw = models.TextField(blank=True, null=True)
