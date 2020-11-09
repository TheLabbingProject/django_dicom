"""
Definition of the :class:`~django_dicom.models.series.Series` class.

"""


import logging
import numpy as np
import os
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
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.utils.fields import ChoiceArrayField
from django_dicom.models.utils import help_text
from django_dicom.models.utils.validators import digits_and_dots_only
from pathlib import Path


class Series(DicomEntity):
    """
    A model to represent a single instance of the Series_ entity.

    .. _Series: http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html

    """

    #: `Series Instance UID
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/0020000e>`_
    #: value.
    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series Instance UID",
        help_text=help_text.SERIES_UID,
    )

    #: `Series Number
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00200011>`_
    #: value.
    number = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Series Number",
        help_text=help_text.SERIES_NUMBER,
    )

    #: `Series Description
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/0008103e>`_
    #: value.
    description = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Series Description",
        help_text=help_text.SERIES_DESCRIPTION,
    )

    #: `Series Date
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00080021>`_
    #: value.
    date = models.DateField(
        blank=True, null=True, help_text=help_text.SERIES_DATE
    )

    #: `Series Time
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00080021>`_
    #: value.
    time = models.TimeField(
        blank=True, null=True, help_text=help_text.SERIES_TIME
    )

    #: `Echo Time
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180081>`_
    #: value.
    echo_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.ECHO_TIME,
    )

    #: `Echo Train Length
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180091>`_
    #: value.
    echo_train_length = models.PositiveIntegerField(
        blank=True, null=True, help_text=help_text.ECHO_TRAIN_LENGTH
    )

    #: `Inversion Time
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180082>`_
    #: value.
    inversion_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.INVERSION_TIME,
    )

    #: `Repetition Time
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180080>`_
    #: value.
    repetition_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.REPETITION_TIME,
    )

    #: `Scanning Sequence
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180020>`_
    #: value.
    scanning_sequence = ChoiceArrayField(
        models.CharField(max_length=2, choices=ScanningSequence.choices()),
        size=5,
        help_text=help_text.SCANNING_SEQUENCE,
        blank=True,
        null=True,
    )

    #: `Sequence Variant
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180021>`_
    #: value.
    sequence_variant = ChoiceArrayField(
        models.CharField(max_length=4, choices=SequenceVariant.choices()),
        size=6,
        help_text=help_text.SEQUENCE_VARIANT,
        blank=True,
        null=True,
    )

    #: `Pixel Spacing
    #: <https://dicom.innolitics.com/ciods/mr-image/image-plane/00280030>`_
    #: value.
    pixel_spacing = ArrayField(
        models.FloatField(validators=[MinValueValidator(0)]),
        size=2,
        help_text=help_text.PIXEL_SPACING,
        blank=True,
        null=True,
    )

    #: `Slice Thickness
    #: <https://dicom.innolitics.com/ciods/mr-image/image-plane/00180050>`_
    #: value.
    slice_thickness = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text=help_text.SLICE_THICKNESS,
        blank=True,
        null=True,
    )

    #: `Manufacturer
    #: <https://dicom.innolitics.com/ciods/mr-image/device/00500010/00080070>`_
    #: value.
    manufacturer = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.MANUFACTURER
    )

    #: `Manufacturer's Model Name
    #: <https://dicom.innolitics.com/ciods/mr-image/device/00500010/00081090>`_
    #: value.
    manufacturer_model_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=help_text.MANUFACTURER_MODEL_NAME,
    )

    #: `Magnetic Field Strength
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180087>`_
    #: value.
    magnetic_field_strength = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.MAGNETIC_FIELD_STRENGTH,
    )

    #: `Device Serial Number
    #: <https://dicom.innolitics.com/ciods/mr-image/device/00500010/00181000>`_
    #: value.
    device_serial_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=help_text.DEVICE_SERIAL_NUMBER,
    )

    #: `Body Part Examined
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00180015>`_
    #: value.
    body_part_examined = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        help_text=help_text.BODY_PART_EXAMINED,
    )

    #: `Patient Position
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00185100>`_
    #: value.
    patient_position = models.CharField(
        max_length=4,
        choices=PatientPosition.choices(),
        blank=True,
        null=True,
        help_text=help_text.PATIENT_POSITION,
    )

    #: `Modality
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00080060>`_
    #: value.
    modality = models.CharField(
        max_length=10, choices=Modality.choices(), help_text=help_text.MODALITY
    )

    #: `Institution Name
    #: <https://dicom.innolitics.com/ciods/mr-image/general-equipment/00080080>`_
    #: value.
    institution_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=help_text.INSTITUTE_NAME,
    )

    #: `Operator's Name
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00081070>`_
    #: value.
    operators_name = models.JSONField(
        blank=True, null=True, help_text=help_text.OPERATORS_NAME
    )

    #: `Protocol Name
    #: <https://dicom.innolitics.com/ciods/mr-image/general-series/00181030>`_
    #: value.
    protocol_name = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.PROTOCOL_NAME
    )

    #: `Flip Angle
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00181314>`_
    #: value.
    flip_angle = models.FloatField(
        null=True, blank=True, help_text=help_text.FLIP_ANGLE
    )

    #: `MR Acquisition Type
    #: <https://dicom.innolitics.com/ciods/mr-image/mr-image/00180023>`_
    #: value.
    MR_ACQUISITION_2D = "2D"
    MR_ACQUISITION_3D = "3D"
    MR_ACQUISITION_TYPE_CHOICES = (
        (MR_ACQUISITION_2D, "2D"),
        (MR_ACQUISITION_3D, "3D"),
    )
    mr_acquisition_type = models.CharField(
        max_length=2,
        choices=MR_ACQUISITION_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text=help_text.MR_ACQUISITION_TYPE,
        verbose_name="MR Acquisition Type",
    )

    #: The :class:`~django_dicom.models.study.Study` instance to which this
    #: series belongs.
    study = models.ForeignKey(
        "django_dicom.Study", on_delete=models.PROTECT, blank=True, null=True
    )

    #: The :class:`~django_dicom.models.patient.Patient` instance to which this
    #: series belongs.
    patient = models.ForeignKey(
        "django_dicom.Patient", on_delete=models.PROTECT, blank=True, null=True
    )

    #: A dictionary of DICOM data element keywords to be used to populate
    #: a created instance's fields.
    FIELD_TO_HEADER = {
        "uid": "SeriesInstanceUID",
        "date": "SeriesDate",
        "time": "SeriesTime",
        "description": "SeriesDescription",
        "number": "SeriesNumber",
        "mr_acquisition_type": "MRAcquisitionType",
    }

    # Cached :class:`~dicom_parser.image.Image` instance.
    _instance = None

    logger = logging.getLogger("data.dicom.series")

    class Meta:
        ordering = (
            "-date",
            "time",
            "number",
        )
        verbose_name_plural = "Series"
        indexes = [
            models.Index(fields=["uid"]),
            models.Index(fields=["date", "time"]),
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
        For more information see the `Django documentation`_.

        .. _Django documentation:
           https://docs.djangoproject.com/en/3.0/ref/models/instances/#get-absolute-url

        Returns
        -------
        str
            This instance's absolute URL path
        """

        return reverse("dicom:series-detail", args=[str(self.id)])

    def save(self, *args, **kwargs) -> None:
        """
        Overrides :meth:`~django_dicom.models.dicom_entity.DicomEntity.save` to
        create any missing related DICOM entities if required.
        """

        header = kwargs.get("header")
        if header and self.missing_relation:
            if not self.patient:
                self.patient, _ = header.get_or_create_patient()
            if not self.study:
                self.study, _ = header.get_or_create_study()
        super().save(*args, **kwargs)

    def get_path(self) -> Path:
        """
        Returns the base directory containing the images composing this series.

        Returns
        -------
        str
            This series's base directory path
        """

        sample_image = self.image_set.first()
        dcm_path = (
            sample_image.dcm.name
            if os.getenv("USE_S3")
            else sample_image.dcm.path
        )
        return Path(dcm_path).parent

    def get_scanning_sequence_display(self) -> list:
        """
        Returns the display valuse of this instance's
        :attr:`~django_dicom.models.series.Series.scanning_sequence` attribute.

        Returns
        -------
        list
            Verbose scanning sequence values
        """

        if self.scanning_sequence:
            return [
                ScanningSequence[sequence].value
                if getattr(ScanningSequence, sequence, False)
                else sequence
                for sequence in self.scanning_sequence
            ]

    def get_sequence_variant_display(self) -> list:
        """
        Returns the display valuse of this instance's
        :attr:`~django_dicom.models.series.Series.sequence_variant` attribute.

        Returns
        -------
        list
            Verbose sequence variant values
        """

        if self.sequence_variant:
            return [
                SequenceVariant[variant].value
                if getattr(SequenceVariant, variant, False)
                else variant
                for variant in self.sequence_variant
            ]

    @property
    def path(self) -> Path:
        """
        Returns the base path of this series' images.

        Returns
        -------
        :class:`pathlib.Path`
            Series directory path
        """

        return self.get_path()

    @property
    def instance(self) -> DicomSeries:
        """
        Caches the created :class:`dicom_parser.series.Series`
        instance to prevent multiple reades.

        Returns
        -------
        :class:`dicom_parser.series.Series`
            Series information
        """

        if not isinstance(self._instance, DicomSeries):
            self._instance = DicomSeries(self.path)
        return self._instance

    @property
    def data(self) -> np.ndarray:
        """
        Returns the :attr:`dicom_parser.series.Series.data` property's value.

        Returns
        -------
        :class:`np.ndarray`
            Series data
        """

        return self.instance.data

    @property
    def datetime(self) -> datetime:
        """
        Returns a :class:`datetime.datetime` object by combining the values of
        the :attr:`~django_dicom.models.series.Series.date` and
        :attr:`~django_dicom.models.series.Series.time` fields.

        Returns
        -------
        :class:`datetime.datetime`
            Series datetime
        """

        time = self.time or datetime.min.time()
        if self.date:
            return datetime.combine(self.date, time, tzinfo=pytz.UTC)

    @property
    def missing_relation(self) -> bool:
        """
        Returns whether this instance misses an associated
        :class:`~django_dicom.models.patient.Patient` or
        :class:`~django_dicom.models.study.Study`.

        Returns
        -------
        bool
            Whether this instance has missing relationships
        """

        return not (self.patient and self.study)

    @property
    def spatial_resolution(self) -> tuple:
        """
        Returns the 3D spatial resolution of the instance by combining the
        values of the :attr:`~django_dicom.models.series.Series.pixel_spacing`
        and :attr:`~django_dicom.models.series.Series.slice_thickness` fields.

        Returns
        -------
        tuple
            (x, y, z) resolution in millimeters
        """

        if self.pixel_spacing and self.slice_thickness:
            return tuple(self.pixel_spacing + [self.slice_thickness])
        elif self.pixel_spacing:
            return tuple(self.pixel_spacing)
