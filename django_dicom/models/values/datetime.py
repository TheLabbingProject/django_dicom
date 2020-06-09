from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class DateTime(DataElementValue):
    value = models.DateTimeField()
    raw = models.CharField(max_length=26, help_text="YYYYMMDDHHMMSS.FFFFFF&ZZXX")
