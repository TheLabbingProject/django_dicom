"""
Utilities for the :mod:`~django_dicom.views` module.
"""
from typing import Dict, Tuple

from django.db.models import Aggregate, Max, Min

CONTENT_DISPOSITION: str = "attachment; filename={name}.zip"
ZIP_CONTENT_TYPE: str = "application/x-zip-compressed"
CSV_COLUMNS: Dict[str, str] = {
    "ID": "id",
    "EchoTime": "echo_time",
    "RepetitionTime": "repetition_time",
    "InversionTime": "inversion_time",
    "PixelSpacing": "pixel_spacing",
    "SliceThickness": "slice_thickness",
    "StudyDescription": "study__description",
    "SequenceName": "sequence_name",
    "PulseSequenceName": "pulse_sequence_name",
    "StudyTime": "study__time",
    "StudyDate": "study__date",
    "Manufacturer": "manufacturer",
    "ScanningSequence": "scanning_sequence",
    "SequenceVariant": "sequence_variant",
}
SERIES_OREDRING_FIELDS: Tuple[str] = (
    "study",
    "patient",
    "number",
    "date",
    "time",
    "scanning_sequence",
    "sequence_variant",
    "pixel_spacing",
    "echo_time",
    "inversion_time",
    "repetition_time",
    "manufacturer",
    "manufacturer_model_name",
    "magnetic_field_strength",
    "device_serial_number",
    "institution_name",
)

SERIES_SEARCH_FIELDS: Tuple[str] = (
    "study",
    "patient",
    "body_part_examined",
    "number",
    "description",
    "date",
    "time",
    "modality",
    "protocol_name",
    "scanning_sequence",
    "sequence_variant",
    "pixel_spacing",
    "echo_time",
    "inversion_time",
    "repetition_time",
    "flip_angle",
    "manufacturer",
    "manufacturer_model_name",
    "magnetic_field_strength",
    "device_serial_number",
    "institution_name",
    "uid",
)

STUDY_AGGREGATIONS: Dict[str, Aggregate] = {
    "nPatientsMin": Min("n_patients"),
    "nPatientsMax": Max("n_patients"),
    "nSeriesMin": Min("n_series"),
    "nSeriesMax": Max("n_series"),
    "nImagesMin": Min("n_images"),
    "nImagesMax": Max("n_images"),
}

PATIENT_AGGREGATIONS: Dict[str, Aggregate] = {
    "nStudiesMin": Min("n_studies"),
    "nStudiesMax": Max("n_studies"),
    "nSeriesMin": Min("n_series"),
    "nSeriesMax": Max("n_series"),
    "nImagesMin": Min("n_images"),
    "nImagesMax": Max("n_images"),
}

