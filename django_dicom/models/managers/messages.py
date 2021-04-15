DATA_ELEMENT_CREATION_FAILURE = (
    "Failed to create DataElement instance for:\n{data_element}\n{exception}"
)
HEADER_CREATION_FAILURE = "Failed to read header information!\n{exception}"
IMPORT_ERROR = (
    "Failed to import {path}\nThe following exception was raised: {exception}"
)
PATIENT_UID_MISMATCH = "Patient UID mismatch! Image {image_uid} is associated with patient {db_value} in the database, but the provided header shows {patient_uid}"

# flake8: noqa: E501
