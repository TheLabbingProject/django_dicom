"""
A utility module used to get the appropriate
:class:`~django_dicom.models.values.data_element_value.DataElementValue`
subclass (*"ValueModel"*) for a given data element.
"""


from dicom_parser.data_element import DataElement as DicomDataElement
from dicom_parser.utils.value_representation import ValueRepresentation
from django_dicom.models.utils.meta import get_model

#: Dictionary with
#: :class:`~dicom_parser.utils.value_representation.ValueRepresentation` items
#: as keys and strings representing the appropriate
#: :class:`~django_dicom.models.values.data_element_value.DataElementValue`
#: subclass as values.
VR_TO_MODEL = {
    ValueRepresentation.AE: "ApplicationEntity",
    ValueRepresentation.AS: "AgeString",
    ValueRepresentation.CS: "CodeString",
    ValueRepresentation.DA: "Date",
    ValueRepresentation.DT: "DateTime",
    ValueRepresentation.DS: "DecimalString",
    ValueRepresentation.FD: "FloatingPointDouble",
    ValueRepresentation.FL: "FloatingPointSingle",
    ValueRepresentation.IS: "IntegerString",
    ValueRepresentation.LO: "LongString",
    ValueRepresentation.LT: "LongText",
    ValueRepresentation.OW: "OtherWord",
    ValueRepresentation.PN: "PersonName",
    ValueRepresentation.SH: "ShortString",
    ValueRepresentation.SL: "SignedLong",
    ValueRepresentation.SQ: "SequenceOfItems",
    ValueRepresentation.SS: "SignedShort",
    ValueRepresentation.ST: "ShortText",
    ValueRepresentation.TM: "Time",
    ValueRepresentation.UI: "UniqueIdentifier",
    ValueRepresentation.UL: "UnsignedLong",
    ValueRepresentation.UN: "Unknown",
    ValueRepresentation.US: "UnsignedShort",
    ValueRepresentation.UT: "UnlimitedText",
}

#: Special cases might require a custom
#: :class:`~django_dicom.models.values.data_element_value.DataElementValue`
#: subclass based on the element's tag rather than its VR.
TAG_TO_MODEL = {("0029", "1010"): "CsaHeader", ("0029", "1020"): "CsaHeader"}


def get_value_model_name(data_element: DicomDataElement) -> str:
    """
    Returns the name of the
    :class:`~django_dicom.models.values.data_element_value.DataElementValue`
    subclass matching the given data element.

    Parameters
    ----------
    data_element : :class:`dicom_parser.data_element.DataElement`
        Object representing a single data element in memory

    Returns
    -------
    str
        Name of the appropriate *"ValueModel"*
    """

    return (
        TAG_TO_MODEL.get(data_element.tag)
        or VR_TO_MODEL[data_element.VALUE_REPRESENTATION]
    )


def get_value_model(data_element: DicomDataElement):
    """
    Returns the
    :class:`~django_dicom.models.values.data_element_value.DataElementValue`
    subclass matching the given data element.

    Parameters
    ----------
    data_element : :class:`dicom_parser.data_element.DataElement`
        Object representing a single data element in memory

    Returns
    -------
    :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        Value model
    """

    model_name = get_value_model_name(data_element)
    return get_model(model_name)
