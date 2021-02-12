"""
Definition of a custom :class:`~django.db.models.Manager` for the
:class:`~django_dicom.models.data_element.DataElement` model.
"""

from dicom_parser.data_element import DataElement as DicomDataElement
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_dicom.exceptions import DicomImportError
from django_dicom.models.data_element_definition import DataElementDefinition
from django_dicom.models.managers.messages import DATA_ELEMENT_CREATION_FAILURE
from django_dicom.models.values.data_element_value import DataElementValue


class DataElementManager(models.Manager):
    """
    Custom :class:`~django.db.models.Manager` for the
    :class:`~django_dicom.models.data_element.DataElement` model.
    """

    def create_from_dicom_parser(
        self, header, definition, data_element: DicomDataElement
    ):
        """
        Creates a new instance under *header* using the provided *definition*
        and *data_element*.

        Parameters
        ----------
        header : :class:`~django_dicom.models.header.Header`
            The header instance with which the created data element should be
            associated.
        definition : :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
            The data element definition of the created data element
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        :class:`~django_dicom.models.data_element.DataElement`
            The created instance


        .. # noqa: E501
        """

        new_instance = self.create(header=header, definition=definition)
        value, _ = DataElementValue.objects.from_dicom_parser(data_element)
        new_instance._values.set(value)
        return new_instance

    def from_dicom_parser(self, header, data_element: DicomDataElement):
        """
        Creates a new instance under *header* using the provided
        :class:`dicom_parser.data_element.DataElement` instance.

        Parameters
        ----------
        header : :class:`~django_dicom.models.header.Header`
            The header instance with which the created data element should be
            associated.
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        :class:`~django_dicom.models.data_element.DataElement`
            The created instance
        """

        definition, _ = DataElementDefinition.objects.from_dicom_parser(data_element)
        try:
            return self.get(header=header, definition=definition)
        except ObjectDoesNotExist:
            try:
                return self.create_from_dicom_parser(header, definition, data_element)
            except TypeError as exception:
                message = DATA_ELEMENT_CREATION_FAILURE.format(
                    data_element=data_element, exception=exception
                )
                raise DicomImportError(message)
