import pandas as pd

from django.db import models
from django_dicom.models.managers.data_element import DataElementManager
from django_dicom.utils.html import Html


class DataElement(models.Model):
    header = models.ForeignKey(
        "django_dicom.Header", on_delete=models.CASCADE, related_name="data_element_set"
    )
    definition = models.ForeignKey(
        "django_dicom.DataElementDefinition",
        on_delete=models.PROTECT,
        related_name="data_element_set",
    )
    _values = models.ManyToManyField(
        "django_dicom.DataElementValue", related_name="data_element_set"
    )

    objects = DataElementManager()

    LIST_ELEMENTS = "ScanningSequence", "SequenceVariant"

    class Meta:
        unique_together = "header", "definition"
        ordering = "header", "definition"
        indexes = [models.Index(fields=["header", "definition"])]

    def __str__(self) -> str:
        series = self.to_verbose_series()
        return "\n" + series.to_string()

    def to_html(self, verbose: bool = False, **kwargs) -> str:
        html = [
            value.to_html(verbose=verbose, **kwargs)
            for value in self._values.select_subclasses()
        ]
        return html.pop() if len(html) == 1 else html

    def dict_key_to_series(self, key: str) -> str:
        return key.replace("_", " ").title() if len(key) > 2 else key.upper()

    def to_verbose_series(self) -> pd.Series:
        d = self.to_verbose_dict()
        d = {self.dict_key_to_series(key): value for key, value in d.items()}
        return pd.Series(d)

    def to_verbose_dict(self) -> dict:
        return {
            "tag": tuple(self.definition.tag),
            "keyword": self.definition.keyword,
            "value_representation": self.definition.value_representation,
            "value": self.value,
        }

    @property
    def admin_link(self) -> str:
        model_name = self.__class__.__name__
        return Html.admin_link(model_name, self.id)

    @property
    def value(self):
        values = self._values.select_subclasses()
        if self.definition.value_representation == "SQ":
            return values.first().header_set.all()
        if values.count() == 1 and self.definition.keyword not in self.LIST_ELEMENTS:
            return values.first().value
        else:
            value = [instance.value for instance in values.all()]
            return value or None

    @property
    def value_multiplicity(self) -> int:
        return self._values.count()
