from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_dicom.models.managers.data_element_value import DataElementValueManager
from django_dicom.utils.html import Html


class DataElementValue(models.Model):
    # If the value is one of a number of values within a DataElement
    # (a DataElement with a value multiplicity that is greater than 1),
    # keep the index of this value.
    index = models.PositiveIntegerField(blank=True, null=True)

    # If any warnings were raised by `dicom_parser`, log them in the database.
    warnings = ArrayField(
        models.TextField(blank=True, null=True), blank=True, null=True
    )

    # Value fields that are meant to be overridden by child models.
    raw = None  # Value as it appears in the DICOM header
    value = None  # Parsed value

    objects = DataElementValueManager()

    class Meta:
        ordering = ["index"]

    def __str__(self) -> str:
        s = str(self.value)
        return f"{s}\n\nWARNING:\n{self.warnings}" if self.warnings else s

    def get_raw_peek(self, size: int = 100) -> str:
        try:
            if len(self.raw) > size:
                return self.raw[:size] + "..."
        except TypeError:
            pass
        return self.raw

    def to_html(self, **kwargs) -> str:
        return self.value

    @property
    def admin_link(self) -> str:
        model_name = self.__class__.__name__
        return Html.admin_link(model_name, self.id)
