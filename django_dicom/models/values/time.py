"""
Definition of the :class:`~django_dicom.models.values.time.Time` model.
"""


from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue


class Time(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *Time* data
    element value.
    """

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    #: to assign a :class:`~django.db.models.TimeField`.
    value = models.TimeField(blank=True, null=True)

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    #: to assign a :class:`~django.db.models.CharField`.
    raw = models.CharField(
        max_length=16, help_text="HHMMSS.FFFFFF", blank=True, null=True
    )

    def to_html(self, **kwargs) -> str:
        """
        Returns the HTML representation of this instance.

        Returns
        -------
        str
            HTML representation of this instance
        """

        return self.value.strftime("%H:%M:%S.%f")


# flake8: noqa: E501
