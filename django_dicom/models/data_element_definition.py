import pandas as pd

from dicom_parser.utils.value_representation import ValueRepresentation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_dicom.models.managers.data_element_definition import (
    DataElementDefinitionManager,
)
from django_dicom.utils.html import Html


class DataElementDefinition(models.Model):
    tag = ArrayField(models.CharField(max_length=4), size=2)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    value_representation = models.CharField(
        max_length=2, choices=ValueRepresentation.choices()
    )
    description = models.TextField()

    objects = DataElementDefinitionManager()

    class Meta:
        indexes = [models.Index(fields=["keyword"])]
        ordering = ("keyword",)
        unique_together = ("tag", "keyword")

    def __str__(self) -> str:
        series = self.to_series()
        return "\n" + series.to_string()

    def to_dict(self) -> dict:
        return {
            "tag": tuple(self.tag),
            "keyword": self.keyword,
            "value_representation": self.value_representation,
            "description": self.description,
        }

    def _normalize_dict_key(self, key: str) -> str:
        return key.replace("_", " ").title() if len(key) > 2 else key.upper()

    def to_series(self) -> pd.Series:
        d = self.to_dict()
        d = {self._normalize_dict_key(key): value for key, value in d.items()}
        return pd.Series(d)

    @property
    def admin_link(self) -> str:
        model_name = self.__class__.__name__
        text = str(tuple(self.tag))
        return Html.admin_link(model_name, self.id, text)
