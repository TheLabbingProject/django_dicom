from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django_dicom.apps import DjangoDicomConfig

digits_and_dots_only = RegexValidator(
    "^\d+(\.\d+)*$", message="Digits and dots only!", code="invalid_uid"
)


def validate_file_extension(value):
    ext = DjangoDicomConfig.data_extension
    if not value.name.endswith(f".{ext}"):
        raise ValidationError(
            f"Invalid file: {value.name}! Only {ext} files are supported."
        )

