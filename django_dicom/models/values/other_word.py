from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_dicom.models.values.data_element_value import DataElementValue


class OtherWord(DataElementValue):
    value = ArrayField(models.IntegerField(), blank=True, null=True)
    raw = models.BinaryField(blank=True, null=True)
