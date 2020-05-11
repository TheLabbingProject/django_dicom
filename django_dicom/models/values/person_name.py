from django.contrib.postgres.fields import JSONField
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.utils.html import Html


class PersonName(DataElementValue):
    value = JSONField(blank=True, null=True)
    raw = models.CharField(max_length=64, blank=True, null=True)

    NAME_STRING_TEMPLATE = (
        "{name_prefix} {given_name} {middle_name} {family_name} {name_suffix}"
    )

    def __str__(self) -> str:
        components = {key: value for key, value in self.value.items()}
        name = self.NAME_STRING_TEMPLATE.format(**components)
        return " ".join(name.strip().split())

    def to_html(self, **kwargs) -> str:
        return Html.json(self.value)
