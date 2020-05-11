from dicom_parser.utils.value_representation import (
    get_value_representation,
    ValueRepresentation,
)
from django.db import DataError
from django_dicom.models.values.vr_to_model import get_value_model
from django_dicom.models.utils.meta import get_model
from model_utils.managers import InheritanceManager
from dicom_parser.data_element import DataElement as DicomDataElement


class DataElementValueManager(InheritanceManager):
    def handle_invalid_data(
        self, ValueModel, data_element: DicomDataElement, error: Exception
    ) -> tuple:
        raw = data_element.raw.value
        value = data_element.value
        info = f"\nRaw value:\n{raw}\nParsed value:\n{value}"
        warning = str(error) + info
        value, created = ValueModel.objects.get_or_create(
            raw=None, value=None, warnings=[warning]
        )
        return [value], created

    def handle_single_value(self, ValueModel, data_element: DicomDataElement) -> tuple:
        value, created = ValueModel.objects.get_or_create(
            index=None,
            raw=data_element.raw.value,
            value=data_element.value,
            warnings=data_element.warnings,
        )
        return [value], created

    def handle_multiple_values(
        self, ValueModel, data_element: DicomDataElement
    ) -> tuple:
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

    def handle_no_value(self, ValueModel) -> tuple:
        value, created = ValueModel.objects.get_or_create(
            index=None, raw=None, value=None, warnings=None
        )
        return [value], created

    def handle_value_multiplicity(
        self, ValueModel, data_element: DicomDataElement,
    ) -> tuple:
        if data_element.value_multiplicity == 1:
            return self.handle_single_value(ValueModel, data_element)
        elif data_element.value_multiplicity > 1:
            return self.handle_multiple_values(ValueModel, data_element)
        else:
            return self.handle_no_value(ValueModel)

    def get_or_create_from_nonsequence(self, data_element: DicomDataElement) -> tuple:
        ValueModel = get_value_model(data_element)
        try:
            return self.handle_value_multiplicity(ValueModel, data_element)
        except (ValueError, DataError) as error:
            return self.handle_invalid_data(ValueModel, data_element, error)

    def from_dicom_parser(self, data_element: DicomDataElement) -> tuple:
        if data_element.VALUE_REPRESENTATION == ValueRepresentation.SQ:
            SequenceOfItems = get_model("SequenceOfItems")
            sequence, created = SequenceOfItems.objects.from_dicom_parser(data_element)
            return [sequence], created
        else:
            return self.get_or_create_from_nonsequence(data_element)
