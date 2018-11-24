from django.core.validators import RegexValidator

digits_and_dots_only = RegexValidator(
    '^\d+(\.\d+)*$',
    message='Digits and dots only!',
    code='invalid_uid',
)
