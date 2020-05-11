from dicom_parser.header import Header as DicomHeader
from django.db import models, transaction
from django_dicom.models.data_element import DataElement
from django_dicom.models.utils.utils import PIXEL_ARRAY_TAG


class HeaderManager(models.Manager):
    def from_dicom_parser(self, header: DicomHeader, **kwargs):
        with transaction.atomic():
            new_instance = self.create(**kwargs)
            for data_element in header.data_elements:
                if data_element.tag != PIXEL_ARRAY_TAG:
                    try:
                        DataElement.objects.from_dicom_parser(
                            new_instance, data_element
                        )
                    except ImportError as e:
                        raise ImportError(
                            f"Failed to read header data for {self.dcm}!\n{e}"
                        )
        return new_instance
