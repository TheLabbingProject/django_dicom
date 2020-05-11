from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class Date(DataElementValue):
    value = models.DateField(blank=True, null=True)
    raw = models.CharField(max_length=8, help_text="YYYYMMDD", blank=True, null=True)
