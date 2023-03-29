"""
Definition of the :class:`SequenceOfItemsManager` class.
"""
from dicom_parser.data_element import DataElement as DicomDataElement
from django_dicom.models.managers.data_element_value import DataElementValueManager
from django_dicom.models.utils.meta import get_model


class SequenceOfItemsManager(DataElementValueManager):
    """
    Custom manager for the
    :class:`~django_dicom.models.values.sequence_of_items.SequenceOfItems`
    model.
    """

    def from_dicom_parser(self, data_element: DicomDataElement) -> tuple:
        """
        Create a sequence of items by reading the included headers and
        populating the database accordingly.

        Parameters
        ----------
        data_element : DicomDataElement
            Sequence of items data element

        Returns
        -------
        Tuple[DataElementValue, bool]
            The data element and whether is was created or not
        """
        Header = get_model("Header")
        sequence = self.create()
        for i_header, dicom_header in enumerate(data_element.value):
            _ = Header.objects.from_dicom_parser(
                dicom_header, parent=sequence, index=i_header
            )
        return sequence, True
