"""
Definition of a custom :class:`~django.db.models.Manager` for the
:class:`~django_dicom.models.data_element_definition.DataElementDefinition`
model.
"""

from dicom_parser.data_element import DataElement as DicomDataElement
from django.db import models


def data_element_to_definition(data_element: DicomDataElement) -> dict:
    """
    Converts a dicom_parser_ :class:`~dicom_parser.data_element.DataElement`
    to a dictionary of keyword arguments that may be used to instantiate
    a
    :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
    instance.

    .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/

    Parameters
    ----------
    data_element : :class:`dicom_parser.data_element.DataElement`
        Object representing a single data element in memory

    Returns
    -------
    dict
        :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
        instantiation keyword arguments
    """

    return {
        "tag": list(data_element.tag),
        "keyword": data_element.keyword,
        "value_representation": data_element.VALUE_REPRESENTATION.name,
        "description": data_element.description,
    }


class DataElementDefinitionManager(models.Manager):
    """
    Custom :class:`~django.db.models.Manager` for the
    :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
    model.
    """

    def from_dicom_parser(self, data_element: DicomDataElement) -> tuple:
        """
        Gets or creates a
        :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
        instance from a dicom_parser_
        :class:`~dicom_parser.data_element.DataElement`.

        .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/

        Parameters
        ----------
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        tuple
            data_element_definition, created
        """

        definition = data_element_to_definition(data_element)
        try:
            existing = self.get(
                tag=definition["tag"], keyword=definition["keyword"]
            )
            return existing, False
        except self.model.DoesNotExist:
            new = self.create(**definition)
            return new, True
