from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class Time(DataElementValue):
    value = models.TimeField(blank=True, null=True)
    raw = models.CharField(
        max_length=16, help_text="HHMMSS.FFFFFF", blank=True, null=True
    )

    def to_html(self, **kwargs) -> str:
        return self.value.strftime("%H:%M:%S.%f")
