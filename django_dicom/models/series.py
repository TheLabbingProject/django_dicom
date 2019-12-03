import json
import numpy as np
import os

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from django_dicom.models import help_text
from django_dicom.reader.code_strings import (
    Modality,
    ScanningSequence,
    SequenceVariant,
    PatientPosition,
)
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models.validators import digits_and_dots_only
from django_dicom.utils import NumpyEncoder


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
    )
    sequence_variant = ChoiceArrayField(
        models.CharField(max_length=4, choices=SequenceVariant.choices()),
        size=6,
        help_text=help_text.SEQUENCE_VARIANT,
    )
    pixel_spacing = ArrayField(
        models.FloatField(validators=[MinValueValidator(0)]),
        size=2,
        help_text=help_text.PIXEL_SPACING,
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

    class Meta:
        ordering = ("number",)
        verbose_name_plural = "Series"
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date", "time"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:series_detail", args=[str(self.id)])

    def get_data(self, as_json: bool = False) -> np.ndarray:
        """
        Returns a NumPy array with the series data.

        Parameters
        ----------
        as_json : bool
            Return the pixel array as a JSON formatted string.        
        
        Returns
        -------
        np.ndarray
            Series pixel array.
        """

        images = self.image_set.order_by("number")
        data = np.stack([image.get_data() for image in images], axis=-1)
        if as_json:
            return json.dumps({"data": data}, cls=NumpyEncoder)
        return data

    def get_path(self) -> str:
        """
        Returns the base directory containing the images composing this series.
        
        Returns
        -------
        str
            This series's base directory path.
        """

        return os.path.dirname(self.image_set.first().dcm.path)

    def get_scanning_sequence_display(self) -> list:
        """
        Returns the :class:`~django_dicom.reader.code_strings.scanning_sequence.ScanningSequence`
        Enum values corresponding to the *scanning_sequence* field's value.
        
        Returns
        -------
        list
            :class:`~django_dicom.reader.code_strings.scanning_sequence.ScanningSequence` Enum values.
        """

        return [ScanningSequence[name].value for name in self.scanning_sequence]

    def get_sequence_variant_display(self) -> list:
        """
        Returns the :class:`~django_dicom.reader.code_strings.sequence_variant.SequenceVariant`
        Enum values corresponding to the *sequence_variant* field's value.
        
        Returns
        -------
        list
            :class:`~django_dicom.reader.code_strings.sequence_variant.SequenceVariant` Enum values.
        """

        return [SequenceVariant[name].value for name in self.sequence_variant]

    def get_gradient_directions(self) -> list:
        """
        Returns the `gradient directions (B-vectors)`_ for `SIEMENS originated DWI`_ DICOM data.
        
        .. _gradient directions (B-vectors): https://na-mic.org/wiki/NAMIC_Wiki:DTI:DICOM_for_DWI_and_DTI#DICOM_for_DWI
        .. _SIEMENS originated DWI: https://na-mic.org/wiki/NAMIC_Wiki:DTI:DICOM_for_DWI_and_DTI#Private_vendor:_Siemens        

        Returns
        -------
        list
            B-vectors for the three dimensions.
        """
        if self.manufacturer == "SIEMENS":
            try:
                return [
                    list(vector)
                    for vector in zip(
                        *[
                            image.gradient_direction
                            for image in self.image_set.order_by("number").all()
                        ]
                    )
                ]
            except TypeError:
                return None
        else:
            raise NotImplementedError(
                f"{self.manufacturer} is not a supported manufacturer for gradient directions retrieval!"
            )

