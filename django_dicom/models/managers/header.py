"""
Definition of a custom :class:`~django.db.models.Manager` for the
:class:`~django_dicom.models.header.Header` model.
"""
from dicom_parser.header import Header as DicomHeader
from django.db import models, transaction
from django_dicom.exceptions import DicomImportError
from django_dicom.models.data_element import DataElement
from django_dicom.models.managers.messages import HEADER_CREATION_FAILURE
from django_dicom.models.utils.utils import check_element_inclusion


class HeaderManager(models.Manager):
    """
    Custom :class:`~django.db.models.Manager` for the
    :class:`~django_dicom.models.header.Header` model.
    """

    def from_dicom_parser(self, header: DicomHeader, **kwargs):
        """
        Creates a new instance from a dicom_parser_
        :class:`dicom_parser.header.Header`.

        .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/

        Parameters
        ----------
        header : :class:`dicom_parser.header.Header`
            Object representing an entire DICOM header in memory

        Returns
        -------
        :class:`django_dicom.models.header.Header`
            Created instance

        Raises
        ------
        DicomImportError
            DICOM header read error
        """

        with transaction.atomic():
            new_instance = self.create(**kwargs)
            for data_element in header.data_elements:
                included_element = check_element_inclusion(data_element)
                if included_element:
                    try:
                        DataElement.objects.from_dicom_parser(
                            new_instance, data_element
                        )
                    except DicomImportError as exception:
                        message = HEADER_CREATION_FAILURE.format(
                            exception=exception
                        )
                        raise DicomImportError(message)
        return new_instance
