"""
Definition of the
:class:`~django_dicom.models.values.data_element_value.DataElementValue`
model.
"""

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_dicom.models.managers.data_element_value import (
    DataElementValueManager,
)
from django_dicom.utils.html import Html


class DataElementValue(models.Model):
    """
    A parent :class:`~django.db.models.Model` representing a single value
    contained by some :class:`~django_dicom.models.data_element.DataElement`
    instance. If the data element has value multiplicity greater than 1, it
    will have multiple instances of this model associated with it, each with
    its own *index* value.
    """

    #: If the value is one of a number of values within a DataElement
    #: (a DataElement with a value multiplicity that is greater than 1),
    #: this field keeps the index of this value.
    index = models.PositiveIntegerField(blank=True, null=True)

    #: If any warnings were raised by `dicom_parser`, log them in the database.
    warnings = ArrayField(
        models.TextField(blank=True, null=True), blank=True, null=True
    )

    #: Raw data element value (meant to be overridden by child models).
    raw = None  # Value as it appears in the DICOM header

    #: Interpreted data element value (meant to be overridden by child models).
    value = None  # Parsed value

    objects = DataElementValueManager()

    class Meta:
        ordering = ["index"]

    def __str__(self) -> str:
        """
        Returns the string representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """

        s = str(self.value)
        return f"{s}\n\nWARNING:\n{self.warnings}" if self.warnings else s

    def get_raw_peek(self, size: int = 100) -> str:
        """
        Returns a truncated string of the raw data element's value (appended
        with *"..."* if changed).

        Parameters
        ----------
        size : int, optional
            Maximal string length, by default 100

        Returns
        -------
        str
            Truncated string
        """

        try:
            if len(self.raw) > size:
                return self.raw[:size] + "..."
        except TypeError:
            pass
        return self.raw

    def to_html(self, **kwargs) -> str:
        """
        Returns the HTML representation of this instance.
        This method simlpy returns the *value*, child models should override
        to provide an appropriate representation.

        Returns
        -------
        str
            HTML representation of this instance
        """

        return self.value

    @property
    def admin_link(self) -> str:
        """
        Creates an HTML tag to link to this instance within the admin site.

        Returns
        -------
        str
            Link to this instance in the admin site
        """

        model_name = self.__class__.__name__
        return Html.admin_link(model_name, self.id)
