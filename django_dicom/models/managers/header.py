from dicom_parser.header import Header as DicomHeader
from django.db import models, transaction
from django_dicom.exceptions import DicomImportError
from django_dicom.models.data_element import DataElement
from django_dicom.models.utils.utils import check_element_inclusion


class HeaderManager(models.Manager):
    def from_dicom_parser(self, header: DicomHeader, **kwargs):
        with transaction.atomic():
            new_instance = self.create(**kwargs)
            for data_element in header.data_elements:
                included_element = check_element_inclusion(data_element)
                if included_element:
                    try:
                        DataElement.objects.from_dicom_parser(
                            new_instance, data_element
                        )
                    except DicomImportError as e:
                        raise DicomImportError(
                            f"Failed to read header data for {self.dcm}!\n{e}"
                        )
        return new_instance
