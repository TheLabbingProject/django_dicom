from django.contrib.postgres.fields import JSONField
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.utils.html import Html


class CsaHeader(DataElementValue):
    raw = models.TextField(blank=True, null=True)
    value = JSONField(blank=True, null=True)

    def to_html(self, verbose: bool = False, **kwargs) -> str:
        if verbose:
            return Html.json(self.value)
        text = f"Csa Header #{self.id}"
        return Html.admin_link("DataElementValue", self.id, text)
