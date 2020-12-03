from dicom_parser.utils.code_strings import ScanningSequence, SequenceVariant
from django_dicom.utils.utils import NegativitiyEnum, FieldsEnum

# fields = {
#     "ScanningSequence": (0x0018, 0x0020),
#     "SequenceVariant": (0x0018, 0x0021),
#     "RepetitionTime": (0x0018, 0x0080),
#     "InversionTime": (0x0018, 0x0082),
#     "PixelSpacing": (0x0028, 0x0030),
#     "SliceThickness": (0x0018, 0x0050),
#     "StudyDescription": (0x0008, 0x1030),
#     "SequenceName": (0x0018, 0x0024),
#     "PulseSequenceName": (0x0018, 0x9005),
#     "StudyTime": (0x0008, 0x0030),
#     "StudyDate": (0x0008, 0x0020),
#     "Manufacturer": (0x0008, 0x0070),
#     "InternalPulseSequenceName": (0x0019, 0x109E),
# }


def header_getter(field, header):
    data_element = header.get_data_element(field)

    dtype = data_element.VALUE_REPRESENTATION.value
    data = data_element.value
    if "String" in dtype and "Decimal" not in dtype and "Code" not in dtype:
        dtype = "STRING"
    elif "Code String" in dtype:
        dtype = "LIST"
    else:
        dtype = "NORMAL"

    if isinstance(data, (tuple, list)):
        data = (
            [ScanningSequence(elem).name for elem in data]
            if field == "ScanningSequence" or field == (0x0018, 0x0020)
            else [SequenceVariant(elem).name for elem in data]
            if field == "SequenceVariant" or field == (0x0018, 0x0021)
            else data
        )
    else:
        data = (
            ScanningSequence(data).name
            if field == "ScanningSequence" or field == (0x0018, 0x0020)
            else SequenceVariant(data).name
            if field == "SequenceVariant" or field == (0x0018, 0x0021)
            else data
        )

    return data or None, dtype


def positive_checker(value, field, header_value):
    if header_value:
        return value == header_value
    return False


def negative_checker(value, field, header_value):
    if header_value:
        return value != header_value
    return False


def positive_string_checker(values, field, header_value):
    if header_value:
        if isinstance(values, (tuple, list)):
            return any(
                value in str(header_value)
                or value.lower() in str(header_value)
                for value in values
            )
        else:
            return values in str(header_value) or values.lower() in str(
                header_value
            )
    return False


def negative_string_checker(values, field, header_value):
    if header_value:
        if isinstance(values, (tuple, list)):
            return not any(
                value in str(header_value)
                or value.lower() in str(header_value)
                for value in values
            )
        else:
            return values not in str(
                header_value
            ) and values.lower() not in str(header_value)
    return False


def positive_list_checker(values, field, header_value):
    if header_value:
        if isinstance(values, (tuple, list)):
            return all(value in header_value for value in values)
        else:
            return values in header_value
    return False


def negative_list_checker(values, field, header_value):
    if header_value:
        if isinstance(values, (tuple, list)):
            return not all(value in header_value for value in values)
        else:
            return values not in header_value
    return False


def run_checks(search_values, header):
    fields_check = [
        field_checker(item, search_values[item], header)
        for item in search_values
    ]
    return all(fields_check)


checkers_list = [
    [positive_checker, positive_list_checker, positive_string_checker],
    [negative_checker, negative_list_checker, negative_string_checker],
]

# checking_fields = {
#     "ScanningSequence": {
#         "positive": positive_list_checker,
#         "negative": negative_list_checker,
#     },
#     "SequenceVariant": {
#         "positive": positive_list_checker,
#         "negative": negative_list_checker,
#     },
#     "SequenceName": {
#         "positive": positive_string_checker,
#         "negative": negative_string_checker,
#     },
#     "InternalPulseSequenceName": {
#         "positive": positive_string_checker,
#         "negative": negative_string_checker,
#     },
#     "InversionTime": {
#         "positive": positive_checker,
#         "negative": negative_checker,
#     },
#     "RepetitionTime": {
#         "positive": positive_checker,
#         "negative": negative_checker,
#     },
#     "Manufacturer": {
#         "positive": positive_checker,
#         "negative": negative_checker,
#     },
#     "PixelSpacing": {
#         "positive": positive_checker,
#         "negative": negative_checker,
#     },
#     "SliceThickness": {
#         "positive": positive_checker,
#         "negative": negative_checker,
#     },
#     "SeriesDescription": {
#         "positive": positive_checker,
#         "negative": negative_checker,
#     },
# }


def field_correction(field):
    first_char = field[0] == "-"
    func = "NEGATIVE" if first_char else "POSITIVE"
    output = field[1:] if first_char else field
    if "(" in output:
        output = [int(tag.strip(), 16) for tag in output[1:-1].split(",")]
        output = tuple(output)

    return func, output


def field_checker(field, value, header):
    func, field = field_correction(field)
    header_value, dtype = header_getter(field, header)
    return checkers_list[NegativitiyEnum[func].value][FieldsEnum[dtype].value](
        value, field, header_value
    )


def scan_details(scan_id, header):
    return {
        "ID": scan_id,
        "RepetitionTime": header_getter("RepetitionTime", header),
        "InversionTime": header_getter("InversionTime", header),
        "PixelSpacing": header_getter("PixelSpacing", header),
        "SliceThickness": header_getter("SliceThickness", header),
        "SeriesDescription": header_getter("SeriesDescription", header),
        "SequenceName": header_getter("SequenceName", header),
        "InternalPulseSequenceName": header_getter(
            "InternalPulseSequenceName", header
        ),
        "StudyTime": header_getter("StudyTime", header),
        "StudyDate": header_getter("StudyDate", header),
        "Manufacturer": header_getter("Manufacturer", header),
        "ScanningSequence": header_getter("ScanningSequence", header),
        "SequenceVariant": header_getter("SequenceVariant", header),
    }
