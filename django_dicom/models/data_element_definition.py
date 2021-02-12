"""
Definition of the :class:`~django_dicom.models.data_element.DataElement` class.

"""

import pandas as pd
from dicom_parser.utils.value_representation import ValueRepresentation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_dicom.models.managers.data_element_definition import \
    DataElementDefinitionManager
from django_dicom.utils.html import Html


class DataElementDefinition(models.Model):
    """
    A model representing a single DICOM data element definition.

    Notes
    -----
    For more information see the `DICOM standard's documentation`_ as well as
    `registry of data elements`_.

    .. _DICOM standard's documentation:
       http://dicom.nema.org/medical/dicom/current/output/chtml/part05/chapter_7.html
    .. _registry of data elements:
       http://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html

    """

    #: Data element tags are an ordered pair of 16-bit unsigned integers
    #: representing the *Group Number* followed by *Element Number* and they
    #: are represented in the database using an array (list) of two four
    #: character strings.
    tag = ArrayField(models.CharField(max_length=4), size=2)

    #: Most data elements have some keyword that facilitates querying header
    #: information.
    keyword = models.CharField(max_length=255, blank=True, null=True)

    #: The value representation (VR) defines the type of information stored in
    #: the data element. This will be used to determine which
    #: :class:`~django_dicom.models.values.data_element_value.DataElementValue`
    #: subclass is instantiated to save this information to the database.
    value_representation = models.CharField(
        max_length=2, choices=ValueRepresentation.choices()
    )

    #: A short description of this data element.
    description = models.TextField()

    objects = DataElementDefinitionManager()

    class Meta:
        indexes = [models.Index(fields=["keyword"])]
        ordering = ("keyword",)
        unique_together = ("tag", "keyword")

    def __str__(self) -> str:
        """
        Returns the str representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """

        series = self.to_series()
        return "\n" + series.to_string()

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of this instance.

        Returns
        -------
        dict
            This instance's dictionary representation
        """

        return {
            "tag": tuple(self.tag),
            "keyword": self.keyword,
            "value_representation": self.value_representation,
            "description": self.description,
        }

    def _normalize_dict_key(self, key: str) -> str:
        """
        Reformats a string from snake case to title case.
        If the string is 2 characters or less assumes acronym or
        abbreviation and simply calls :meth:`~str.upper`.

        Parameters
        ----------
        key : str
            Snake case dictionary key representing some field name

        Returns
        -------
        str
            Title cased string
        """

        return key.replace("_", " ").title() if len(key) > 2 else key.upper()

    def to_series(self) -> pd.Series:
        """
        Returns a :class:`~pandas.Series` representation of this instance.

        Returns
        -------
        :class:`pandas.Series`
            Series representation of this instance
        """

        d = self.to_dict()
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
        text = str(tuple(self.tag))
        return Html.admin_link(model_name, self.id, text)
