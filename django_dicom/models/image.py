"""
Definition of the :class:`~django_dicom.models.image.Image` class.

"""

import dicom_parser
import logging
import numpy as np
import warnings

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.header import Header
from django_dicom.models.managers.image import ImageManager
from django_dicom.models.series import Series
from django_dicom.models.validators import digits_and_dots_only, validate_file_extension
from django_dicom.models.utils import get_dicom_root
from pathlib import Path

DICOM_ROOT = get_dicom_root()


class Image(DicomEntity):
    """
    A model to represent a single DICOM_ image. This model is meant to be
    instantiated with the `file` field set to some *.dcm* file, and then it is
    updated automatically by inspection of the file's header information.

    .. _DICOM: https://www.dicomstandard.org/

    """

    # Stores a reference to the image file.
    dcm = models.FileField(
        max_length=1000,
        upload_to="dicom",
        validators=[validate_file_extension],
        verbose_name="File Path",
    )
    header = models.OneToOneField(
        "django_dicom.Header", on_delete=models.CASCADE, related_name="image"
    )

    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Image UID",
    )
    number = models.IntegerField(verbose_name="Image Number", null=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    warnings = ArrayField(models.TextField(), blank=True, null=True, default=list)

    series = models.ForeignKey(
        "django_dicom.Series", on_delete=models.PROTECT, blank=True, null=True
    )

    objects = ImageManager()

    _instance = None
    FIELD_TO_HEADER = {
        "uid": "SOPInstanceUID",
        "number": "InstanceNumber",
        "date": "InstanceCreationDate",
        "time": "InstanceCreationTime",
    }

    logger = logging.getLogger("data.dicom.image")

    class Meta:
        ordering = ("series", "number")
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date", "time"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:image-detail", args=[str(self.id)])

    def create_header_instance(self) -> Header:
        return Header.objects.from_dicom_parser(self.instance.header)

    def save(self, *args, rename: bool = True, **kwargs):
        if self.dcm and not hasattr(self, "header"):
            # Add the create Header instance to the passed kwargs
            # so that it may be used to update the new image instance's
            # fields in DicomEntity's `save()` execution.
            self.header = self.create_header_instance()
            kwargs["header"] = self.header

        if not self.series and "header" in kwargs:
            self.series, _ = Series.objects.from_header(kwargs["header"])
        if self.dcm and rename:
            # Move to default destination.
            self.rename(self.default_path)
        super().save(*args, **kwargs)

    def get_default_path(self) -> Path:
        relative_path = self.instance.default_relative_path
        return DICOM_ROOT / relative_path

    def rename(self, target: Path) -> Path:
        target = Path(settings.MEDIA_ROOT, target)
        target.parent.mkdir(parents=True, exist_ok=True)
        p = Path(self.dcm.path)
        p.rename(target)
        self.dcm = str(target)

    @property
    def instance(self) -> dicom_parser.Image:
        """
        Caches the created :class:`dicom_parser.image.Image`
        instance to prevent multiple reades.

        Returns
        -------
        :class:`~dicom_parser.image.Image`
            The image's information.
        """

        if not isinstance(self._instance, dicom_parser.Image):
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                try:
                    self._instance = dicom_parser.Image(self.dcm.path)
                except Warning as warning:
                    if str(warning) not in self.warnings:
                        self.warnings += [str(warning)]
                    warnings.filterwarnings("ignore")
                    self._instance = dicom_parser.Image(self.dcm.path)
        return self._instance

    @property
    def data(self) -> np.ndarray:
        """
        Facilitates access to the :class:`~dicom_parser.image.Image` instance's
        data.

        Returns
        -------
        np.ndarray
            The image's pixel data.
        """

        return self.instance.data

    @property
    def default_path(self) -> Path:
        return self.get_default_path()
