import numpy as np
import os

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from django.urls import reverse
from django_dicom.interfaces.dcm2niix import Dcm2niix
from django_dicom.models import help_text
from django_dicom.models.code_strings import (
    Modality,
    ScanningSequence,
    SequenceVariant,
    PatientPosition,
)
from django_dicom.models.dicom_entity import DicomEntity, DicomEntityManager
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models.nifti import NIfTI
from django_dicom.models.study import Study
from django_dicom.models.validators import digits_and_dots_only
from django_dicom.utils import snake_case_to_camel_case


class SeriesManager(DicomEntityManager):
    UID_FIELD = "series_uid"

    def get_anatomicals(self, by_date: bool = False):
        anatomicals = self.filter(
            scanning_sequence=[Series.GRADIENT_RECALLED, Series.INVERSION_RECOVERY]
        ).order_by("date", "time")
        if by_date:
            dates = anatomicals.values_list("date", flat=True).distinct()
            return {date: anatomicals.filter(date=date) for date in dates}
        return anatomicals

    def get_default_anatomical(self):
        return (
            self.get_anatomicals(by_date=False)
            .order_by("-date", "pixel_spacing__0", "pixel_spacing__1")
            .first()
        )

    def get_anatomicals_by_pixel_spacing(self, pixel_spacing: list):
        return (
            self.get_anatomicals()
            .filter(pixel_spacing=pixel_spacing)
            .order_by("-date", "description")
        )

    def get_inversion_recovery(self, by_date: bool = False):
        inversion_recovery = self.filter(
            scanning_sequence=[Series.ECHO_PLANAR, Series.INVERSION_RECOVERY],
            repetition_time__gt=6000,
        )
        if by_date:
            dates = inversion_recovery.values_list("date", flat=True).distinct()
            return {date: inversion_recovery.filter(date=date) for date in dates}
        return inversion_recovery

    def get_latest_inversion_recovery_sequence(self):
        return self.get_inversion_recovery(by_date=False).order_by(
            "-date", "inversion_time"
        )


class Series(DicomEntity):
    series_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series UID",
    )
    date = models.DateField(help_text=help_text.SERIES_DATE, blank=True, null=True)
    time = models.TimeField(help_text=help_text.SERIES_TIME, blank=True, null=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    number = models.IntegerField(
        verbose_name="Series Number",
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    echo_time = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )
    inversion_time = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )
    repetition_time = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )
    scanning_sequence = ChoiceArrayField(
        models.CharField(max_length=2, choices=ScanningSequence.choices()),
        size=5,
        blank=True,
        null=True,
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
    manufacturer = models.CharField(max_length=64, blank=True, null=True)
    manufacturer_model_name = models.CharField(max_length=64, blank=True, null=True)
    magnetic_field_strength = models.FloatField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    device_serial_number = models.CharField(max_length=64, blank=True, null=True)
    body_part_examined = models.CharField(max_length=16, blank=True, null=True)
    patient_position = models.CharField(
        max_length=4,
        choices=PatientPosition.choices(),
        default=PatientPosition.HFS.name,
    )
    modality = models.CharField(
        max_length=10, choices=Modality.choices(), default=Modality.MR.name
    )
    institution_name = models.CharField(max_length=64, blank=True, null=True)
    protocol_name = models.CharField(max_length=64, blank=True, null=True)
    flip_angle = models.FloatField(null=True, blank=True)
    MR_ACQUISITION_2D = "2D"
    MR_ACQUISITION_3D = "3D"
    MR_ACQUISITION_TYPE_CHOICES = ((MR_ACQUISITION_2D, "2D"), (MR_ACQUISITION_3D, "3D"))
    mr_acquisition_type = models.CharField(
        max_length=2, choices=MR_ACQUISITION_TYPE_CHOICES, default=MR_ACQUISITION_2D
    )
    _nifti = models.OneToOneField(
        "django_dicom.nifti", on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    study = models.ForeignKey(Study, blank=True, null=True, on_delete=models.PROTECT)
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
        return np.stack(
            [instance.read_data().pixel_array for instance in instances], axis=-1
        )

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

    # def relate_entity(self, model: DicomEntity) -> DicomEntity:
    #     field_name = self.get_related_entity_field_name(model)
    #     is_unique = self.check_uniqueness_in_instance_set(field_name)
    #     if is_unique:
    #         sample_instance = self.instance_set.last()
    #         entity_instance = sample_instance.get_or_create_related_entity(model)
    #         setattr(self, field_name, entity_instance)
    #     else:
    #         raise IntegrityError(f"Failed to determine {field_name}!")

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
