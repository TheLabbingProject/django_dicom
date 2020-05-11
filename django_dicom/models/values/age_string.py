from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class AgeString(DataElementValue):
    value = models.FloatField(verbose_name="Age in years", blank=True, null=True)
    raw = models.CharField(max_length=4, blank=True, null=True)
