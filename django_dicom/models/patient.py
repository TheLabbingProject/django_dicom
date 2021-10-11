"""
Definition of the :class:`Patient` class.
"""
import logging

from dicom_parser.utils.code_strings import Sex
from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers.patient import PatientQuerySet


class Patient(DicomEntity):
    """
    A model to represent a single instance of the Patient_ entity.

    .. _Patient:
       http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html
    """

    #: `Patient ID
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100020>`_
    #: value.
    uid = models.CharField(
        max_length=64, unique=True, verbose_name="Patient UID"
    )

    #: `Patient Birth Date
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100030>`_
    #: value.
    date_of_birth = models.DateField(blank=True, null=True)

    #: `Patient's Sex
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100040>`_
    #: value.
    sex = models.CharField(
        max_length=1, choices=Sex.choices(), blank=True, null=True
    )

    #: `Patient's Name
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100010>`_
    #: value.
    given_name = models.CharField(max_length=64, blank=True, null=True)
    #: `Patient's Name
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100010>`_
    #: value.
    family_name = models.CharField(max_length=64, blank=True, null=True)
    #: `Patient's Name
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100010>`_
    #: value.
    middle_name = models.CharField(max_length=64, blank=True, null=True)
    #: `Patient's Name
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100010>`_
    #: value.
    name_prefix = models.CharField(max_length=64, blank=True, null=True)
    #: `Patient's Name
    #: <https://dicom.innolitics.com/ciods/mr-image/patient/00100010>`_
    #: value.
    name_suffix = models.CharField(max_length=64, blank=True, null=True)

    #: A dictionary of DICOM data element keywords to be used to populate
    #: a created instance's fields.
    FIELD_TO_HEADER = {
        "uid": "PatientID",
        "date_of_birth": "PatientBirthDate",
        "sex": "PatientSex",
    }

    # A list of the different name parts that make a Patient Name data element
    _NAME_PARTS = [
        "given_name",
        "family_name",
        "middle_name",
        "name_prefix",
        "name_suffix",
    ]

    logger = logging.getLogger("data.dicom.patient")

    objects = PatientQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["uid"]),
            models.Index(fields=["date_of_birth"]),
        ]

    def __str__(self) -> str:
        """
        Returns the str representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """
        return self.uid

    def get_absolute_url(self) -> str:
        """
        Returns the absolute URL for this instance.

        Returns
        -------
        str
            This instance's absolute URL path
        """
        return reverse("dicom:patient-detail", args=[str(self.id)])

    def get_full_name(self) -> str:
        """
        Returns the first and last names of the patient.

        Returns
        -------
        str
            Patient's first and last names.
        """
        return f"{self.given_name} {self.family_name}"

    def update_patient_name(self, header) -> None:
        """
        Parses the patient's name from the DICOM header and updates the
        instance's fields.

        Parameters
        ----------
        header : :class:`~dicom_parser.header.Header`
            A DICOM image's :class:`~dicom_parser.header.Header` instance.
        """

        patient_name = header.instance.get("PatientName", {})
        for part, value in patient_name.items():
            setattr(self, part, value)

    def update_fields_from_header(self, header, exclude: list = None) -> None:
        """
        Overrides
        :meth:`~django_dicom.model.dicom_entity.DicomEntity.update_fields_from_header`
        to handle setting the name parts.

        Parameters
        ----------
        header : :class:`~dicom_parser.header.Header`
            DICOM header information.
        exclude : list, optional
            Field names to exclude (the default is [], which will not exclude
            any header fields).
        """
        # Exclude PatientName fields
        if isinstance(exclude, list):
            exclude += self._NAME_PARTS
        else:
            exclude = self._NAME_PARTS
        super().update_fields_from_header(header, exclude=exclude)
        # Handle PatientName fields
        self.update_patient_name(header)
        # Validate valid sex value
        if self.sex not in Sex.__members__:
            self.sex = None

    def query_n_studies(self) -> int:
        """
        Returns the number of associated studies.

        See Also
        --------
        :func:`n_studies`

        Returns
        -------
        int
            Number of associated studies
        """
        return self.series_set.values("study").distinct().count()

    def query_n_images(self) -> int:
        """
        Returns the number of associated images.

        See Also
        --------
        :func:`n_images`

        Returns
        -------
        int
            Number of associated images
        """
        return self.series_set.values("image").count()

    @property
    def n_studies(self) -> int:
        """
        Returns the number of associated studies.

        See Also
        --------
        :func:`query_n_studies`

        Returns
        -------
        int
            Number of associated studies
        """
        return self.query_n_studies()

    @property
    def n_series(self) -> int:
        """
        Returns the number of associated series.

        Returns
        -------
        int
            Number of associated series
        """
        return self.series_set.count()

    @property
    def n_images(self) -> int:
        """
        Returns the number of associated images.

        See Also
        --------
        :func:`query_n_images`

        Returns
        -------
        int
            Number of associated images
        """
        return self.query_n_images()
