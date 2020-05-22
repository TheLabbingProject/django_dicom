from django.db import models

from django.core.exceptions import ObjectDoesNotExist
from django_dicom.exceptions import ImportError
from django_dicom.models.data_element_definition import DataElementDefinition
from django_dicom.models.values.data_element_value import DataElementValue
from dicom_parser.data_element import DataElement as DicomDataElement


class DataElementManager(models.Manager):
    def create_from_dicom_parser(
        self, header, definition, data_element: DicomDataElement
    ):
        new_instance = self.create(header=header, definition=definition)
        value, _ = DataElementValue.objects.from_dicom_parser(data_element)
        new_instance._values.set(value)
        return new_instance

    def from_dicom_parser(self, header, data_element: DicomDataElement) -> tuple:
        definition, _ = DataElementDefinition.objects.from_dicom_parser(data_element)
        try:
            return self.get(header=header, definition=definition)
        except ObjectDoesNotExist:
            try:
                return self.create_from_dicom_parser(header, definition, data_element)
            except TypeError as e:
                raise ImportError(
                    f"Failed to create DataElement instance for:\n{data_element}\n{e}"
                )
