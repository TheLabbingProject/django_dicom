from dicom_parser.data_element import DataElement as DicomDataElement
from django_dicom.models.managers.data_element_value import DataElementValueManager
from django_dicom.models.utils.meta import get_model


class SequenceOfItemsManager(DataElementValueManager):
    def from_dicom_parser(self, data_element: DicomDataElement) -> tuple:
        Header = get_model("Header")
        sequence = self.create()
        for i_header, dicom_header in enumerate(data_element.value):
            _ = Header.objects.from_dicom_parser(
                dicom_header, parent=sequence, index=i_header
            )
        return sequence, True
