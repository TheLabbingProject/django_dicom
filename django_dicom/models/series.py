import numpy as np
import os

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django_dicom.interfaces.dcm2niix import Dcm2niix
from django_dicom.models import help_text
from django_dicom.models.code_strings import (
    Modality,
    ScanningSequence,
    SequenceVariant,
    PatientPosition,
)
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models.managers import SeriesManager
from django_dicom.models.nifti import NIfTI
from django_dicom.models.validators import digits_and_dots_only
from django_dicom.utils import snake_case_to_camel_case


class Series(DicomEntity):
    series_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series UID",
        help_text=help_text.SERIES_UID,
    )
    date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Series Date",
        help_text=help_text.SERIES_DATE,
    )
    time = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Series Time",
        help_text=help_text.SERIES_TIME,
    )
    description = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Series Description",
        help_text=help_text.SERIES_DESCRIPTION,
    )
    number = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name="Series Number",
        help_text=help_text.SERIES_NUMBER,
    )
    echo_time = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=help_text.ECHO_TIME,
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
        blank=True,
        null=True,
        help_text=help_text.SCANNING_SEQUENCE,
    )
    sequence_variant = ChoiceArrayField(
        models.CharField(max_length=4, choices=SequenceVariant.choices()),
        blank=True,
        null=True,
        help_text=help_text.SEQUENCE_VARIANT,
    )
    pixel_spacing = ArrayField(
        models.FloatField(validators=[MinValueValidator(0)]),
        size=2,
        blank=True,
        null=True,
        help_text=help_text.PIXEL_SPACING,
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
        default=PatientPosition.HFS.name,
        blank=True,
        null=True,
        help_text=help_text.PATIENT_POSITION,
    )
    modality = models.CharField(
        max_length=10,
        choices=Modality.choices(),
        default=Modality.MR.name,
        blank=True,
        null=True,
        help_text=help_text.MODALITY,
    )
    institution_name = models.CharField(
        max_length=64, blank=True, null=True, help_text=help_text.INSTITUTE_NAME
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
        default=MR_ACQUISITION_2D,
        blank=True,
        null=True,
        help_text=help_text.MR_ACQUISITION_TYPE,
    )
    is_updated = models.BooleanField(
        default=False, help_text="Series fields were updated from instance headers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    _nifti = models.OneToOneField(
        "django_dicom.nifti", on_delete=models.CASCADE, blank=True, null=True
    )
    study = models.ForeignKey(
        "django_dicom.Study", blank=True, null=True, on_delete=models.PROTECT
    )
    patient = models.ForeignKey(
        "django_dicom.Patient", blank=True, null=True, on_delete=models.PROTECT
    )

    objects = SeriesManager()

    NIfTI_DIR_NAME = "NIfTI"
    FIELD_TO_HEADER = {
        "series_uid": "SeriesInstanceUID",
        "date": "SeriesDate",
        "time": "SeriesTime",
        "description": "SeriesDescription",
        "number": "SeriesNumber",
        "mr_acquisition_type": "MRAcquisitionType",
    }

    def __str__(self):
        return self.series_uid

    def get_absolute_url(self):
        return reverse("dicom:series_detail", args=[str(self.id)])

    def get_data(self) -> np.ndarray:
        instances = self.instance_set.order_by("number")
        return np.stack([instance.get_data() for instance in instances], axis=-1)

    def to_tree_node(self) -> dict:
        return {
            "id": f"series_{self.id}",
            "icon": "fas fa-flushed",
            "text": self.description,
        }

    def update_fields_from_header(self, force=False):
        for field in self.get_model_header_fields():
            not_null = getattr(self, field.name, False)
            if not force and not_null:
                continue
            header_name = self.FIELD_TO_HEADER.get(
                field.name
            ) or snake_case_to_camel_case(field.name)
            value = self.get_series_attribute(header_name)
            if value:
                setattr(self, field.name, value)
        self.is_updated = True

    def get_path(self):
        return os.path.dirname(self.instance_set.first().file.path)

    def get_default_nifti_dir(self):
        patient_directory = os.path.dirname(self.get_path())
        return os.path.join(patient_directory, self.NIfTI_DIR_NAME)

    def get_default_nifti_name(self):
        return str(self.id)

    def get_default_nifti_destination(self):
        directory = self.get_default_nifti_dir()
        name = self.get_default_nifti_name()
        return os.path.join(directory, name)

    def create_nifti_instance(self, path: str) -> NIfTI:
        nifti_instance = NIfTI(path=path)
        nifti_instance.save()
        return nifti_instance

    def associate_nifti_instance(self, instance: NIfTI) -> NIfTI:
        self._nifti = instance
        self.save()
        return self._nifti

    def to_nifti(self, destination: str = None):
        dcm2niix = Dcm2niix()
        destination = destination or self.get_default_nifti_destination()
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        nifti_path = dcm2niix.convert(self.get_path(), destination)
        nifti_instance = self.create_nifti_instance(nifti_path)
        self.associate_nifti_instance(nifti_instance)
        return self._nifti

    def get_header_values(self, tag_or_keyword, parsed=False) -> list:
        return [
            instance.get_header_value(tag_or_keyword, parsed)
            for instance in self.instance_set.order_by("number").all()
        ]

    def get_distinct_values(self, tag_or_keyword, parsed=False) -> list:
        values = self.get_header_values(tag_or_keyword, parsed=parsed)
        if any(values):
            try:
                return list(set(values))
            except TypeError:
                unique = []
                for value in values:
                    if value not in unique:
                        unique += [value]
                return unique
        return None

    def get_series_attribute(self, tag_or_keyword: str):
        distinct = self.get_distinct_values(tag_or_keyword, parsed=True)
        if distinct is not None and len(distinct) == 1:
            return distinct.pop()
        elif distinct is not None and len(distinct) > 1:
            return distinct
        return None

    def get_scanning_sequence_display(self) -> list:
        return [ScanningSequence[name].value for name in self.scanning_sequence]

    def get_sequence_variant_display(self) -> list:
        return [SequenceVariant[name].value for name in self.sequence_variant]

    def get_gradient_directions(self):
        try:
            return [
                list(vector)
                for vector in zip(
                    *[
                        instance.gradient_direction
                        for instance in self.instance_set.order_by("number").all()
                    ]
                )
            ]
        except TypeError:
            return None

    def get_related_entity_field_name(self, model: DicomEntity) -> str:
        return model.__name__.lower()

    def has_relation(self, model: DicomEntity) -> bool:
        field_name = self.get_related_entity_field_name(model)
        value = getattr(self, field_name, None)
        if isinstance(value, model):
            return True
        return False

    def relate_entity(self, entity_instance: DicomEntity):
        model = type(entity_instance)
        field_name = self.get_related_entity_field_name(model)
        setattr(self, field_name, entity_instance)

    def check_uniqueness_in_instance_set(self, field_name: str) -> bool:
        distinct_count = self.instance_set.values(field_name).distinct().count()
        if distinct_count != 1:
            return False
        return True

    class Meta:
        verbose_name_plural = "Series"
        indexes = [
            models.Index(fields=["series_uid"]),
            models.Index(fields=["date", "time"]),
        ]

    @property
    def nifti(self):
        if self._nifti:
            return self._nifti
        return self.to_nifti()

    @property
    def has_instances(self):
        return bool(self.instance_set.count())
