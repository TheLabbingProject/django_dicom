"""
Definition of the
:class:`~django_dicom.models.values.other_word.OtherWord` model.
"""


from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_dicom.models.values.data_element_value import DataElementValue


class OtherWord(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *OtherWord*
    data element value.
    """

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    #: to assign a :class:`~django.contrib.postgres.fields.ArrayField`.
    value = ArrayField(models.IntegerField(), blank=True, null=True)

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    #: to assign a :class:`~django.db.models.BinaryField`.
    raw = models.BinaryField(blank=True, null=True)


# flake8: noqa: E501
