"""
Definition of the
:class:`~django_dicom.models.values.integer_string.IntegerString` model.
"""


from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue

#: Minimal *IntegerString* value.
MIN_VALUE = -(2 ** 31)
#: Maximal *IntegerString* value.
MAX_VALUE = 2 ** 31 - 1


class IntegerString(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *IntegerString*
    data element value.
    """

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    #: to assign a :class:`~django.db.models.IntegerField`.
    value = models.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ],
        blank=True,
        null=True,
    )

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    #: to assign a :class:`~django.db.models.CharField`.
    raw = models.CharField(max_length=12, blank=True, null=True)


# flake8: noqa: E501
