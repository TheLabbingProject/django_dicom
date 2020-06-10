"""
Definition of the
:class:`~django_dicom.models.values.person_name.PersonName` model.
"""


from django.contrib.postgres.fields import JSONField
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.utils.html import Html


class PersonName(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single *PersonName*
    data element value.
    """

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    #: to assign a :class:`~django.contrib.postgres.fields.JSONField`.
    value = JSONField(blank=True, null=True)

    #: Overrides
    #: :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    #: to assign a :class:`~django.db.models.CharField`.
    raw = models.CharField(max_length=64, blank=True, null=True)

    # String representation template for a PersonName instance.
    _NAME_STRING_TEMPLATE = (
        "{name_prefix} {given_name} {middle_name} {family_name} {name_suffix}"
    )

    def __str__(self) -> str:
        """
        Returns the str representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """

        components = {key: value for key, value in self.value.items()}
        name = self._NAME_STRING_TEMPLATE.format(**components)
        return " ".join(name.strip().split())

    def to_html(self, **kwargs) -> str:
        """
        Returns the HTML representation of this instance.

        Returns
        -------
        str
            HTML representation of this instance
        """

        return Html.json(self.value)


# flake8: noqa: E501
