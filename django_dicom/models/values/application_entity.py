from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class ApplicationEntity(DataElementValue):
    value = models.CharField(max_length=16, blank=True, null=True)
    raw = models.CharField(max_length=16, blank=True, null=True)
