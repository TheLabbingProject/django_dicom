from dicom_parser.data_element import DataElement as DicomDataElement
from dicom_parser.utils.value_representation import ValueRepresentation
from django_dicom.models.utils.meta import get_model


VR_TO_MODEL = {
    ValueRepresentation.AE: "ApplicationEntity",
    ValueRepresentation.AS: "AgeString",
    ValueRepresentation.CS: "CodeString",
    ValueRepresentation.DA: "Date",
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

TAG_TO_MODEL = {("0029", "1010"): "CsaHeader", ("0029", "1020"): "CsaHeader"}


def get_value_model_name(data_element: DicomDataElement) -> str:
    return (
        TAG_TO_MODEL.get(data_element.tag)
        or VR_TO_MODEL[data_element.VALUE_REPRESENTATION]
    )


def get_value_model(data_element: DicomDataElement):
    model_name = get_value_model_name(data_element)
    return get_model(model_name)
