"""
Definition of the :class:`~django_dicom.models.header.Header` class.

"""
import os

from dicom_parser.header import Header as DicomHeader
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers.header import HeaderManager
from django_dicom.models.patient import Patient
from django_dicom.models.series import Series
from django_dicom.models.study import Study
from django_dicom.utils.html import Html
from model_utils.models import TimeStampedModel
from typing import Any, List


class Header(TimeStampedModel):
    """
    A model representing a single DICOM `Data Set`_.

    .. _Data Set:
       http://dicom.nema.org/medical/dicom/current/output/chtml/part05/chapter_7.html

    """

    #: `Data Set
    #: <http://dicom.nema.org/medical/dicom/current/output/chtml/part05/chapter_7.html>`_\s
    #: `may be nested
    #: <http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.5.html>`_.
    #: If this header (Data Set) is
    #: `an item of some sequence
    #: <http://dicom.nema.org/medical/dicom/2017e/output/chtml/part05/sect_7.5.2.html>`_,
    #: this field holds that reference.
    parent = models.ForeignKey(
        "django_dicom.SequenceOfItems",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    #: This Data Set's index in the sequence (if *parent* is not None).
    index = models.PositiveIntegerField(blank=True, null=True)

    # Cached :class:`~dicom_parser.header.Header` instance.
    _instance = None

    objects = HeaderManager()

    def to_verbose_list(self) -> List[dict]:
        """
        Returns a list of dictionaries containing the information from the
        data elements in this header.

        Returns
        -------
        List[dict]
            Header information as a list of dictionaries
        """

        return [
            data_element.to_verbose_dict()
            for data_element in self.data_element_set.all()
        ]

    def to_html(self, verbose: bool = False, **kwargs) -> str:
        """
        Returns an HTML representation of this instance.

        Parameters
        ----------
        verbose : bool, optional
            Whether to return a JSON with all of the header information or just
            a link to this instance's admin page, by default False.

        Returns
        -------
        str
            HTML representaion of this instance
        """

        if verbose:
            return Html.json(self.to_verbose_list())
        text = f"Header #{self.id}"
        return Html.admin_link("Header", self.id, text)

    def get_value_by_keyword(self, keyword: str) -> Any:
        """
        Returns a data element's value by keyword **from the database**
        (not from the DICOM header itself, ergo only elements that are saved
        to the database may be queried).

        Parameters
        ----------
        keyword : str
            Data element keyword

        Returns
        -------
        Any
            Data element value
        """

        try:
            data_element = self.data_element_set.get(
                definition__keyword=keyword
            )
        except ObjectDoesNotExist:
            return None
        else:
            return data_element.value

    def get_entity_uid(self, entity: DicomEntity) -> str:
        """
        Returns the UID of the provided DICOM entity from the header
        information.

        Parameters
        ----------
        entity : :class:`~django_dicom.models.dicom_entity.DicomEntity`
            The entity for which a UID is desired

        Returns
        -------
        str
            The provided DICOM entity's unique identifier
        """

        keyword = entity.get_header_keyword("uid")
        return self.instance.get(keyword)

    def get_or_create_entity(self, entity: DicomEntity) -> tuple:
        """
        Get or create a DICOM entity's instance from this header.

        Parameters
        ----------
        entity : :class:`~django_dicom.models.dicom_entity.DicomEntity`
            The desired DICOM entity's model

        Returns
        -------
        tuple
            instance, creatd
        """

        return entity.objects.from_header(self)

    def get_or_create_series(self) -> tuple:
        """
        Get or create the :class:`~django_dicom.models.series.Series` instance
        corresponding to this header.

        Returns
        -------
        tuple
            instance, created
        """

        return self.get_or_create_entity(Series)

    def get_or_create_patient(self) -> tuple:
        """
        Get or create the :class:`~django_dicom.models.patient.Patient`
        instance corresponding to this header.

        Returns
        -------
        tuple
            instance, created
        """

        return self.get_or_create_entity(Patient)

    def get_or_create_study(self) -> tuple:
        """
        Get or create the :class:`~django_dicom.models.study.Study` instance
        corresponding to this header.

        Returns
        -------
        tuple
            instance, created
        """

        return self.get_or_create_entity(Study)

    @property
    def instance(self) -> DicomHeader:
        """
        Caches the created :class:`dicom_parser.header.Header` instance to
        prevent multiple reades.

        Returns
        -------
        :class:`dicom_parser.header.Header`
            Header information
        """

        if not isinstance(self._instance, DicomHeader):
            dcm_path = (
                self.image.dcm.name
                if os.getenv("USE_S3")
                else self.image.dcm.path
            )
            self._instance = DicomHeader(dcm_path)
        return self._instance

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
