"""
Definition of the :class:`~django_dicom.models.values.unknown.Unknown` model.
"""


from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class Unknown(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *Unknown* data
    element value.
    """

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    #: to assign a :class:`~django.db.models.TextField`.
    value = models.TextField(blank=True, null=True)

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    #: to assign a :class:`~django.db.models.TextField`.
    raw = models.TextField(blank=True, null=True)


# flake8: noqa: E501
