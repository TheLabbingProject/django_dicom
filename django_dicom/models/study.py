"""
Definition of the :class:`Study` class.
"""
import logging

from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers.study import StudyQuerySet
from django_dicom.models.managers.dicom_entity import DicomEntityManager
from django_dicom.models.utils.validators import digits_and_dots_only


class Study(DicomEntity):
    """
    A model to represent a single instance of the Study_ entity.

    .. _Study:
       http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html

    """

    #: `Study Instance UID
    #: <https://dicom.innolitics.com/ciods/mr-image/general-study/0020000d>`_
    #: value.
    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Study Instance UID",
    )

    #: `Study Description
    #: <https://dicom.innolitics.com/ciods/mr-image/general-study/00081030>`_
    #: value.
    description = models.CharField(max_length=64, blank=True, null=True)

    #: `Study Date
    #: <https://dicom.innolitics.com/ciods/mr-image/general-study/00080020>`_
    #: value.
    date = models.DateField(blank=True, null=True)

    #: `Study Time
    #: <https://dicom.innolitics.com/ciods/mr-image/general-study/00080030>`_
    #: value.
    time = models.TimeField(blank=True, null=True)

    #: A dictionary of DICOM data element keywords to be used to populate
    #: a created instance's fields.
    FIELD_TO_HEADER = {
        "uid": "StudyInstanceUID",
        "date": "StudyDate",
        "time": "StudyTime",
        "description": "StudyDescription",
    }

    logger = logging.getLogger("data.dicom.study")

    objects = DicomEntityManager.from_queryset(StudyQuerySet)()

    class Meta:
        verbose_name_plural = "Studies"
        indexes = [models.Index(fields=["uid"])]

    def __str__(self) -> str:
        """
        Returns the str representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """

        return self.uid

    def get_absolute_url(self):
        """
        Returns the absolute URL for this instance.
        For more information see the `Django documentation`_.

        .. _Django documentation:
           https://docs.djangoproject.com/en/3.0/ref/models/instances/#get-absolute-url

        Returns
        -------
        str
            This instance's absolute URL path
        """

        return reverse("dicom:study-detail", args=[str(self.id)])

    def query_n_patients(self) -> int:
        """
        Returns the number of associated patients.

        See Also
        --------
        :func:`n_patients`

        Returns
        -------
        int
            Number of associated patients
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
    def n_patients(self) -> int:
        """
        Returns the number of associated patients.

        See Also
        --------
        :func:`query_n_patients`

        Returns
        -------
        int
            Number of associated patients
        """
        return self.query_n_patients()

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
