from django.db import models
from dicom_parser.data_element import DataElement as DicomDataElement


def data_element_to_definition(data_element: DicomDataElement) -> dict:
    return {
        "tag": list(data_element.tag),
        "keyword": data_element.keyword,
        "value_representation": data_element.VALUE_REPRESENTATION.name,
        "description": data_element.description,
    }


class DataElementDefinitionManager(models.Manager):
    def from_dicom_parser(self, data_element: DicomDataElement) -> tuple:
        definition = data_element_to_definition(data_element)
        try:
            existing = self.get(tag=definition["tag"], keyword=definition["keyword"])
            return existing, False
        except self.model.DoesNotExist:
            new = self.create(**definition)
            return new, True
