"""
Definition of the :class:`DataElement` class.

"""

from typing import Any

import pandas as pd
from django.db import models
from django_dicom.models.managers.data_element import DataElementManager
from django_dicom.utils.html import Html


class DataElement(models.Model):
    """
    A model representing a single `DICOM data element`_.

    Each :class:`~django_dicom.models.data_element.DataElement` instance
    belongs to a :class:`~django_dicom.models.header.Header`, and each
    :class:`~django_dicom.models.header.Header` belongs to an
    :class:`~django_dicom.models.image.Image` or
    :class:`~django_dicom.models.values.sequence_of_items.SequenceOfItems`.

    While the :class:`~django_dicom.models.data_element.DataElement` instance
    holds the reference to the associated models, the defining characteristics
    of the data element are saved as a
    :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
    instance and the values are saved as
    :class:`~django_dicom.models.values.data_element_value.DataElementValue`
    subclass instances in order to prevent data duplication.

    .. _DICOM data element:
       http://dicom.nema.org/medical/dicom/current/output/chtml/part05/chapter_7.html
    """

    #: The :class:`~django_dicom.models.header.Header` instance to which this
    #: data element belongs.
    header = models.ForeignKey(
        "django_dicom.Header",
        on_delete=models.CASCADE,
        related_name="data_element_set",
    )

    #: The
    #: :class:`~django_dicom.models.data_element_definition.DataElementDefinition` # noqa: E501
    #: instance holding information about this element's DICOM tag.
    definition = models.ForeignKey(
        "django_dicom.DataElementDefinition",
        on_delete=models.PROTECT,
        related_name="data_element_set",
    )

    # Holds a reference to the values (multiple in case value multiplicity
    # is greater than 1).
    _values = models.ManyToManyField(
        "django_dicom.DataElementValue", related_name="data_element_set"
    )

    objects = DataElementManager()

    _LIST_ELEMENTS = "ScanningSequence", "SequenceVariant"

    class Meta:
        unique_together = "header", "definition"
        ordering = "header", "definition"

    def __str__(self) -> str:
        """
        Returns the str representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """

        series = self.to_verbose_series()
        return "\n" + series.to_string()

    def _normalize_dict_key(self, key: str) -> str:
        """
        Fixes a given field name to better suit a :class:`pandas.Series` name.

        Parameters
        ----------
        key : str
            Field name as dictionary key

        Returns
        -------
        str
            Formatted field name
        """

        return key.replace("_", " ").title() if len(key) > 2 else key.upper()

    def to_html(self, **kwargs) -> str:
        """
        Returns an HTML representation of this instance.

        Any keyword arguments will be passed to the associated
        :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        subclass instances.

        Returns
        -------
        str
            HTML representaion of this instance
        """

        values = self._values.select_subclasses()
        html = [value.to_html(**kwargs) for value in values]
        return html.pop() if len(html) == 1 else html

    def to_verbose_dict(self) -> dict:
        """
        Returns a dictionary representation of this instance.

        Returns
        -------
        dict
            This instance's information
        """

        return {
            "tag": tuple(self.definition.tag),
            "keyword": self.definition.keyword,
            "value_representation": self.definition.value_representation,
            "value": self.value,
        }

    def to_verbose_series(self) -> pd.Series:
        """
        Returns a :class:`~pandas.Series` representation of this instance.

        Returns
        -------
        :class:`pandas.Series`
            This instance's information
        """

        d = self.to_verbose_dict()
        d = {self._normalize_dict_key(key): value for key, value in d.items()}
        return pd.Series(d)

    @property
    def admin_link(self) -> str:
        """
        Returns an HTML tag linking to this instance in the admin site.

        Returns
        -------
        str
            HTML link to this instance
        """

        model_name = self.__class__.__name__
        return Html.admin_link(model_name, self.id)

    @property
    def value(self) -> Any:
        """
        Returns the value or values (according to the `value multiplicity`_) of
        the associated
        :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        instances.

        .. _value multiplicity:
           http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_6.4.html

        Returns
        -------
        Any
            Data element value
        """

        values = self._values.select_subclasses()

        # If this data element's definition has a value representation of SQ
        # (Sequence of Items), it will have a single value (a SequenceOfItems
        # instance) associating it with the array of headers contained by it.
        is_sequence = self.definition.value_representation == "SQ"
        if is_sequence:
            return values.first().header_set.all()

        # In general, if there is only a single value, it is returned as it is.
        # Some elements, however, are expected to be returned as lists, and
        # therefore are excluded.
        not_list_element = self.definition.keyword not in self._LIST_ELEMENTS
        if values.count() == 1 and not_list_element:
            return values.first().value

        # If there are multiple associated DataElementValue instances, or the
        # element definition's key is listed as a list element, return a list
        # of the values.
        else:
            value = [instance.value for instance in values.all()]

        # If no DataElementValue instances are associated with this
        # DataElement, return None
        return value or None

    @property
    def value_multiplicity(self) -> int:
        """
        Returns the number of
        :class:`~django_dicom.models.values.data_element_value.DataElementValue`
        related to this instance.

        Returns
        -------
        int
            Value multiplicity

        Hint
        ----
        For more information see the DICOM standard's definition of `value
        multiplicity`_.

        .. _value multiplicity:
           http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_6.4.html
        """

        return self._values.count()
