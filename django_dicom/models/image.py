import dicom_parser
import numpy as np

from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.validators import digits_and_dots_only, validate_file_extension


class Image(DicomEntity):
    """
    A model to represent a single DICOM_ image. This model is meant to be
    instantiated with the `file` field set to some *.dcm* file, and then it is
    updated automatically by inspection of the file's header information.

    .. _DICOM: https://www.dicomstandard.org/

    """

    # Stores a reference to the image file.
    dcm = models.FileField(
        max_length=1000, upload_to="dicom", validators=[validate_file_extension]
    )

    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Image UID",
    )
    number = models.IntegerField(verbose_name="Image Number")
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    series = models.ForeignKey("django_dicom.Series", on_delete=models.PROTECT)

    _instance = None
    FIELD_TO_HEADER = {
        "uid": "SOPInstanceUID",
        "number": "InstanceNumber",
        "date": "InstanceCreationDate",
        "time": "InstanceCreationTime",
    }

    class Meta:
        ordering = ["-id"]
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date", "time"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:image-detail", args=[str(self.id)])

    @property
    def instance(self) -> dicom_parser.Image:
        """
        Caches the created :class:`dicom_parser.image.Image`
        instance to prevent multiple reades.

        Returns
        -------
        :class:`dicom_parser.image.Image`
            The image's information.
        """

        if not isinstance(self._instance, dicom_parser.Image):
            self._instance = dicom_parser.Image(self.dcm.path)
        return self._instance

    @property
    def header(self) -> dicom_parser.Header:
        """
        Facilitates access to the :class:`dicom_parser.image.Image` instance's
        associated :class:`~dicom_parser.header.Header` data.

        Returns
        -------
        :class:`~dicom_parser.header.Header`
            The image's header information.
        """

        return self.instance.header

    @property
    def data(self) -> np.ndarray:
        """
        Facilitates access to the :class:`dicom_parser.image.Image` instance's
        data.

        Returns
        -------
        np.ndarray
            The image's pixel data.
        """

        return self.instance.data
