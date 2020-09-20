"""
Definition of the :class:`~django_dicom.models.image.Image` class.

"""

import dicom_parser
import logging
import numpy as np
import os
import warnings
import shutil

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.header import Header
from django_dicom.models.managers.image import ImageManager
from django_dicom.models.series import Series
from django_dicom.models.utils import get_dicom_root
from django_dicom.models.utils.validators import (
    digits_and_dots_only,
    validate_file_extension,
)
from pathlib import Path

DICOM_ROOT = get_dicom_root()


class Image(DicomEntity):
    """
    A model to represent a single instance of the Image_ entity.
    This model is normally instantiated with the
    :attr:`~django_dicom.models.image.Image.dcm` field set to some *.dcm* file
    from which the header information is read.

    .. _Image: http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html

    """

    #: A reference to the DICOM image file.
    dcm = models.FileField(
        max_length=1000,
        upload_to="dicom",
        validators=[validate_file_extension],
        verbose_name="File Path",
    )

    #: The associated :class:`~django_dicom.models.header.Header` instance
    #: representing this image's header information.
    header = models.OneToOneField(
        "django_dicom.Header", on_delete=models.CASCADE, related_name="image"
    )

    #: `SOP Instance UID
    #: <https://dicom.innolitics.com/ciods/mr-image/sop-common/00080018>`_
    #: value.
    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="SOP Instance UID",
    )

    #: `Instance Number
    #: <https://dicom.innolitics.com/ciods/mr-image/general-image/00200013>`_
    #: value.
    number = models.IntegerField(verbose_name="Instance Number", null=True)

    #: `Instance Creation Date
    #: <https://dicom.innolitics.com/ciods/mr-image/sop-common/00080012>`_
    #: value.
    date = models.DateField(
        blank=True, null=True, verbose_name="Instance Creation Date"
    )

    #: `Instance Creation Time
    #: <https://dicom.innolitics.com/ciods/mr-image/sop-common/00080013>`_
    #: value.
    time = models.TimeField(
        blank=True, null=True, verbose_name="Instance Creation Time"
    )

    #: In case any warnings are raised by
    #: `dicom_parser <https://github.com/ZviBaratz/dicom_parser/>`_ upon
    #: reading the image's header information, they are stored in this field.
    warnings = ArrayField(
        models.TextField(), blank=True, null=True, default=list
    )

    #: The :class:`~django_dicom.models.series.Series` instance to which this
    #: image belongs.
    series = models.ForeignKey(
        "django_dicom.Series", on_delete=models.PROTECT, blank=True, null=True
    )

    objects = ImageManager()

    # Cached :class:`~dicom_parser.image.Image` instance.
    _instance = None

    #: A dictionary of DICOM data element keywords to be used to populate
    #: a created instance's fields.
    FIELD_TO_HEADER = {
        "uid": "SOPInstanceUID",
        "number": "InstanceNumber",
        "date": "InstanceCreationDate",
        "time": "InstanceCreationTime",
    }

    logger = logging.getLogger("data.dicom.image")

    class Meta:
        ordering = ("series", "number")
        indexes = [
            models.Index(fields=["uid"]),
            models.Index(fields=["date", "time"]),
        ]

    def __str__(self) -> str:
        """
        Returns the string representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """

        return self.uid

    def get_absolute_url(self) -> str:
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

        return reverse("dicom:image-detail", args=[str(self.id)])

    def create_header_instance(self) -> Header:
        """
        Creates a :class:`~django_dicom.models.header.Header` instance from a
        :class:`dicom_parser.header.Header`.

        Returns
        -------
        :class:`~django_dicom.models.header.Header`
            Created instance
        """

        return Header.objects.from_dicom_parser(self.instance.header)

    def save(self, *args, rename: bool = True, **kwargs):
        """
        Overrides :meth:`~django_dicom.models.dicom_entity.DicomEntity.save` to
        check for missing header information or associated DICOM entities and
        create them if a *.dcm* file is provided.

        Parameters
        ----------
        rename : bool, optional
            Whether to move the file this instance is a reference to to a
            default path under MEDIA_ROOT or not, by default True
        """

        if self.dcm and not hasattr(self, "header"):
            # Add the created Header instance to the passed kwargs
            # so that it may be used to update the new image instance's
            # fields in DicomEntity's `save()` execution.
            self.header = self.create_header_instance()
            kwargs["header"] = self.header

        if not self.series and "header" in kwargs:
            self.series, created_series = Series.objects.from_header(
                kwargs["header"]
            )
        if self.dcm and rename:
            # Move to default destination.
            self.rename(self.default_path)
        super().save(*args, **kwargs)
        # If the associated Series instance is new, invoke save() again so that
        # any signals relying on header data may use the created image's
        # header.
        if created_series:
            self.series.save()

    def get_default_path(self) -> Path:
        """
        Returns a unique default path under MEDIA_ROOT_ for this instance based
        on its header information.

        .. _MEDIA_ROOT:
           https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-MEDIA_ROOT

        Returns
        -------
        :class:`pathlib.Path`
            This instance's default location
        """

        relative_path = self.instance.default_relative_path
        return DICOM_ROOT / relative_path

    def rename(self, target: Path) -> None:
        """
        Move the *.dcm* file this instance references to some target
        destination.

        Parameters
        ----------
        target : :class:`pathlib.Path`
            Destination path
        """

        target = Path(settings.MEDIA_ROOT, target)
        target.parent.mkdir(parents=True, exist_ok=True)
        dcm_path = self.dcm.name if os.getenv("USE_S3") else self.dcm.path
        p = Path(dcm_path)
        if getattr(settings, "KEEP_ORIGINAL_DICOM", False):
            shutil.copy(str(p), str(target))
        else:
            p.rename(target)
        self.dcm = str(target)

    @property
    def instance(self) -> dicom_parser.Image:
        """
        Caches the created :class:`dicom_parser.image.Image` instance to
        prevent multiple reads.

        Returns
        -------
        :class:`dicom_parser.image.Image`
            Image information
        """

        if not isinstance(self._instance, dicom_parser.Image):

            # Catch any warnings raised by dicom_parser
            with warnings.catch_warnings():
                using_s3 = os.getenv("USE_S3")
                dcm_path = self.dcm.name if using_s3 else self.dcm.path
                warnings.filterwarnings("error")
                try:
                    self._instance = dicom_parser.Image(dcm_path)
                # Store raised warnings in the appropriate field
                except Warning as warning:
                    if str(warning) not in self.warnings:
                        self.warnings += [str(warning)]
                    warnings.filterwarnings("ignore")
                    self._instance = dicom_parser.Image(dcm_path)
        return self._instance

    @property
    def data(self) -> np.ndarray:
        """
        Facilitates access to the :class:`~dicom_parser.image.Image` instance's
        data.

        Returns
        -------
        :class:`np.ndarray`
            The image's pixel data
        """

        return self.instance.data

    @property
    def default_path(self) -> Path:
        """
        Default unique path for this image based on its header information.

        Returns
        -------
        :class:`pathlib.Path`
            Default image location
        """

        return self.get_default_path()
