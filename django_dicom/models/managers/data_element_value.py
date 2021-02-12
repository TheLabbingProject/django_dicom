"""
Definition of a custom :class:`~model_utils.managers.InheritanceManager` for
the :class:`~django_dicom.models.values.data_element_value.DataElementValue`
model.

For more information about the
:class:`~model_utils.managers.InheritanceManager` class, see
django-model-utils_\'s `InheritanceManager documentation`_.

.. _django-model-utils: https://github.com/jazzband/django-model-utils
.. _InheritanceManager documentation:
   https://django-model-utils.readthedocs.io/en/latest/managers.html#inheritancemanager
"""

from typing import Tuple

from dicom_parser.data_element import DataElement as DicomDataElement
from dicom_parser.utils.value_representation import ValueRepresentation
from django.db import DataError
from django_dicom.models.utils.meta import get_model
from django_dicom.models.values.vr_to_model import get_value_model
from model_utils.managers import InheritanceManager


class DataElementValueManager(InheritanceManager):
    """
    Custom :class:`~model_utils.managers.InheritanceManager` for the
    :class:`~django_dicom.models.values.data_element_value.DataElementValue`
    model.
    """

    def handle_invalid_data(
        self, ValueModel, data_element: DicomDataElement, error: Exception
    ) -> Tuple:
        """
        If reading the value from the data element using dicom_parser_ raises
        an exception, this method is called to create an "empty" instance of
        the *ValueModel* (i.e. with
        :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
        and
        :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
        set to *None*) and log the exception in the
        :attr:`~django_dicom.models.values.data_element_value.DataElementValue.warnings`
        field.

        .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/

        Parameters
        ----------
        ValueModel : :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            Some
            :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            subclass used to instatiate values
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory
        error : Exception
            The raised exception

        Returns
        -------
        tuple
            data_element_value, created


        .. # noqa: E501
        """

        raw = data_element.raw.value
        value = data_element.value
        info = f"\nRaw value:\n{raw}\nParsed value:\n{value}"
        warning = str(error) + info
        value, created = ValueModel.objects.get_or_create(
            raw=None, value=None, warnings=[warning]
        )
        return [value], created

    def handle_single_value(self, ValueModel, data_element: DicomDataElement) -> tuple:
        """
        Handles data elements with a
        :attr:`~dicom_parser.data_element.DataElement.value_multiplicity` of 1.

        Parameters
        ----------
        ValueModel : :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            Some
            :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            subclass used to instatiate values
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        Tuple[DataElementValue, bool]
            data_element_value, created


        .. # noqa: E501
        """

        value, created = ValueModel.objects.get_or_create(
            index=None,
            raw=data_element.raw.value,
            value=data_element.value,
            warnings=data_element.warnings,
        )
        return [value], created

    def handle_multiple_values(
        self, ValueModel, data_element: DicomDataElement
    ) -> Tuple[list, bool]:
        """
        Handles data elements with a
        :attr:`~dicom_parser.data_element.DataElement.value_multiplicity`
        greater than 1.

        Parameters
        ----------
        ValueModel : :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            Some
            :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            subclass used to instatiate values
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        Tuple[List[DataElementValue, ...], bool]
            data_element_values, any_created


        .. # noqa: E501
        """

        tuples = [
            ValueModel.objects.get_or_create(
                index=i,
                raw=data_element.raw.value[i],
                value=data_element.value[i],
                warnings=data_element.warnings,
            )
            for i in range(len(data_element.raw.value))
        ]
        values = [value[0] for value in tuples]
        created = any([value[1] for value in tuples])
        return values, created

    def handle_no_value(self, ValueModel) -> Tuple:
        """
        Handles data elements with a
        :attr:`~dicom_parser.data_element.DataElement.value_multiplicity` of 0.
        Returns an "empty" instance of
        the *ValueModel* (i.e. with
        :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
        and
        :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
        set to *None*).

        Parameters
        ----------
        ValueModel : :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            Some
            :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            subclass used to instatiate values

        Returns
        -------
        Tuple[DicomDataElement, bool]
            dicom_data_element, created


        .. # noqa: E501
        """

        value, created = ValueModel.objects.get_or_create(
            index=None, raw=None, value=None, warnings=None
        )
        return [value], created

    def handle_value_multiplicity(
        self, ValueModel, data_element: DicomDataElement,
    ) -> Tuple:
        """
        Handles the creation of the
        :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        subclass instances according to the dicom_parser_
        :class:`~dicom_parser.data_element.DataElement`\'s
        :attr:`~dicom_parser.data_element.DataElement.value_multiplicity`
        attribute.

        .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/
        .. # noqa: E501

        Parameters
        ----------
        ValueModel : :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            Some
            :class:`~django_dicom.models.values.data_element_value.DataElementValue`
            subclass used to instatiate values
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        Tuple[Union[DataElementValue, List[DataElementValue, ...]], bool]
            data_element_value or data_element_values, created


        .. # noqa: E501
        """

        if data_element.value_multiplicity == 1:
            return self.handle_single_value(ValueModel, data_element)
        elif data_element.value_multiplicity > 1:
            return self.handle_multiple_values(ValueModel, data_element)
        else:
            return self.handle_no_value(ValueModel)

    def get_or_create_from_nonsequence(self, data_element: DicomDataElement) -> Tuple:
        """
        Get or create some
        :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        subclass instances from a non-*Sequence of Items* dicom_parser_
        :class:`~dicom_parser.data_element.DataElement`.

        .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/

        Parameters
        ----------
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        Tuple[Union[DataElementValue, List[DataElementValue, ...]], bool]
            data_element_value or data_element_values, created
        """

        ValueModel = get_value_model(data_element)
        try:
            return self.handle_value_multiplicity(ValueModel, data_element)
        except (ValueError, DataError) as error:
            return self.handle_invalid_data(ValueModel, data_element, error)

    def from_dicom_parser(self, data_element: DicomDataElement) -> Tuple:
        """
        Get or create some
        :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        subclass instances from a dicom_parser_
        :class:`~dicom_parser.data_element.DataElement`.

        .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/

        Parameters
        ----------
        data_element : :class:`dicom_parser.data_element.DataElement`
            Object representing a single data element in memory

        Returns
        -------
        Tuple[Union[DataElementValue, List[DataElementValue, ...]], bool]
            data_element_value or data_element_values, created
        """

        # Handle SequenceOfItems data elements (i.e. data elements containing
        # an array of nested headers).
        if data_element.VALUE_REPRESENTATION == ValueRepresentation.SQ:
            SequenceOfItems = get_model("SequenceOfItems")
            sequence, created = SequenceOfItems.objects.from_dicom_parser(data_element)
            return [sequence], created
        # Handle all other data elements.
        else:
            return self.get_or_create_from_nonsequence(data_element)
