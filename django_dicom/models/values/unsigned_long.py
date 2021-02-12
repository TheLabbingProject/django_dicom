"""
Definition of the
:class:`~django_dicom.models.values.unsigned_long.UnsignedLong` model.
"""


from django.core.validators import MaxValueValidator
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue

#: Maximal *UnsignedLong* value.
MAX_VALUE = 2 ** 32


class UnsignedLong(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *UnsignedLong*
    data element value.
    """

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    #: to assign a :class:`~django.db.models.PositiveIntegerField`.
    value = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_VALUE)], blank=True, null=True
    )

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    #: to assign a :class:`~django.db.models.PositiveIntegerField`.
    raw = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_VALUE)], blank=True, null=True
    )


# flake8: noqa: E501
