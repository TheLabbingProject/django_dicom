import numpy as np
import pytz

from datetime import datetime
from dicom_parser.series import Series as DicomSeries
from dicom_parser.utils.code_strings import (
    Modality,
    ScanningSequence,
    SequenceVariant,
    PatientPosition,
)
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django_dicom.models import help_text
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models.validators import digits_and_dots_only
from pathlib import Path


class Series(DicomEntity):
    """
    A model to represent DICOM_'s `series entity`_. Holds the corresponding
    attributes as discovered in created :class:`django_dicom.Image` instances.

    .. _DICOM: https://www.dicomstandard.org/
    .. _series entity: http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html

    """

    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series UID",
        help_text=help_text.SERIES_UID,
    )
    number = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Series Number",
        help_text=help_text.SERIES_NUMBER,
    )
    description = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Series Description",
        help_text=help_text.SERIES_DESCRIPTION,
    )
    date = models.DateField(blank=True, null=True, help_text=help_text.SERIES_DATE)
    time = models.TimeField(blank=True, null=True, help_text=help_text.SERIES_TIME)
    echo_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.ECHO_TIME,
    )
    echo_train_length = models.PositiveIntegerField(
        blank=True, null=True, help_text=help_text.ECHO_TRAIN_LENGTH
    )
    inversion_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.INVERSION_TIME,
    )
    repetition_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.REPETITION_TIME,
    )
    scanning_sequence = ChoiceArrayField(
        models.CharField(max_length=2, choices=ScanningSequence.choices()),
        size=5,
        help_text=help_text.SCANNING_SEQUENCE,
        blank=True,
        null=True,
    )
    sequence_variant = ChoiceArrayField(
        models.CharField(max_length=4, choices=SequenceVariant.choices()),
        size=6,
        help_text=help_text.SEQUENCE_VARIANT,
        blank=True,
        null=True,
    )
    pixel_spacing = ArrayField(
        models.FloatField(validators=[MinValueValidator(0)]),
        size=2,
        help_text=help_text.PIXEL_SPACING,
        blank=True,
        null=True,
    )
    slice_thickness = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text=help_text.SLICE_THICKNESS,
        blank=True,
        null=True,
    )
    manufacturer = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.MANUFACTURER
    )
    manufacturer_model_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=help_text.MANUFACTURER_MODEL_NAME,
    )
    magnetic_field_strength = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.MAGNETIC_FIELD_STRENGTH,
    )
    device_serial_number = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.DEVICE_SERIAL_NUMBER
    )
    body_part_examined = models.CharField(
        max_length=16, blank=True, null=True, help_text=help_text.BODY_PART_EXAMINED
    )
    patient_position = models.CharField(
        max_length=4,
        choices=PatientPosition.choices(),
        blank=True,
        null=True,
        help_text=help_text.PATIENT_POSITION,
    )
    modality = models.CharField(
        max_length=10, choices=Modality.choices(), help_text=help_text.MODALITY
    )
    institution_name = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.INSTITUTE_NAME
    )
    operators_name = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.OPERATORS_NAME
    )
    protocol_name = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.PROTOCOL_NAME
    )
    flip_angle = models.FloatField(
        null=True, blank=True, help_text=help_text.FLIP_ANGLE
    )
    MR_ACQUISITION_2D = "2D"
    MR_ACQUISITION_3D = "3D"
    MR_ACQUISITION_TYPE_CHOICES = ((MR_ACQUISITION_2D, "2D"), (MR_ACQUISITION_3D, "3D"))
    mr_acquisition_type = models.CharField(
        max_length=2,
        choices=MR_ACQUISITION_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text=help_text.MR_ACQUISITION_TYPE,
    )

    study = models.ForeignKey("django_dicom.Study", on_delete=models.PROTECT)
    patient = models.ForeignKey(
        "django_dicom.Patient", blank=True, null=True, on_delete=models.PROTECT
    )

    FIELD_TO_HEADER = {
        "uid": "SeriesInstanceUID",
        "date": "SeriesDate",
        "time": "SeriesTime",
        "description": "SeriesDescription",
        "number": "SeriesNumber",
        "mr_acquisition_type": "MRAcquisitionType",
    }
    _instance = None

    class Meta:
        ordering = ("number",)
        verbose_name_plural = "Series"
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date", "time"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:series-detail", args=[str(self.id)])

    def get_path(self) -> Path:
        """
        Returns the base directory containing the images composing this series.

        Returns
        -------
        str
            This series's base directory path.
        """

        return Path(self.image_set.first().dcm.path).parent

    @property
    def path(self) -> Path:
        return self.get_path()

    @property
    def instance(self) -> DicomSeries:
        """
        Caches the created :class:`dicom_parser.series.Series`
        instance to prevent multiple reades.

        Returns
        -------
        :class:`dicom_parser.series.Series`
            The series' information.
        """

        if not isinstance(self._instance, DicomSeries):
            self._instance = DicomSeries(self.path)
        return self._instance

    @property
    def data(self) -> np.ndarray:
        return self.instance.data

    @property
    def datetime(self) -> datetime:
        time = self.time or datetime.min.time()
        if self.date:
            return datetime.combine(self.date, time, tzinfo=pytz.UTC)
