import numpy as np
import os
import subprocess

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django_dicom.apps import DjangoDicomConfig
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models import help_text
from django_dicom.models.code_strings import (
    Modality,
    ScanningSequence,
    SequenceVariant,
    PatientPosition,
)
from django_dicom.models.nifti import NIfTI
from django_dicom.models.study import Study
from django_dicom.models.validators import digits_and_dots_only


class SeriesManager(models.Manager):
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


def to_list(value) -> list:
    if type(value) is str:
        return [value]
    else:
        return list(value)


def replace_underscores_with_spaces(value: str):
    return value.replace("_", " ")


def float_list(value: list):
    return [float(dim_value) for dim_value in value]


class Series(models.Model):
    objects = SeriesManager()

    series_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series UID",
    )
    date = models.DateField(help_text=help_text.SERIES_DATE)
    time = models.TimeField(help_text=help_text.SERIES_TIME)
    description = models.CharField(max_length=64)
    number = models.IntegerField(
        verbose_name="Series Number", validators=[MinValueValidator(0)]
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
    manufacturers_model_name = models.CharField(max_length=64, blank=True, null=True)
    magnetic_field_strength = models.FloatField(validators=[MinValueValidator(0)])
    device_serial_number = models.CharField(max_length=64, blank=True, null=True)
    body_part_examined = models.CharField(max_length=16, blank=True, null=True)

    patient_position = models.CharField(
        max_length=4,
        choices=PatientPosition.choices(),
        default=PatientPosition.HFS.name,
    )

    MR_ACQUISITION_2D = "2D"
    MR_ACQUISITION_3D = "3D"
    MR_ACQUISITION_TYPE_CHOICES = ((MR_ACQUISITION_2D, "2D"), (MR_ACQUISITION_3D, "3D"))
    mr_acquisition_type = models.CharField(
        max_length=2, choices=MR_ACQUISITION_TYPE_CHOICES, default=MR_ACQUISITION_2D
    )
    modality = models.CharField(
        max_length=10, choices=Modality.choices(), default=Modality.MR.name
    )

    nifti = models.OneToOneField(
        "django_dicom.nifti", on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    study = models.ForeignKey(Study, blank=True, null=True, on_delete=models.PROTECT)
    patient = models.ForeignKey(
        "django_dicom.Patient", blank=True, null=True, on_delete=models.PROTECT
    )

    ATTRIBUTE_FORMATTING = {
        "InstanceNumber": int,
        "InversionTime": float,
        "EchoTime": float,
        "RepetitionTime": float,
        "PixelBandwidth": float,
        "SAR": float,
        "FlipAngle": float,
        "ScanningSequence": to_list,
        "Manufacturer": str.capitalize,
        "ManufacturersModelName": str.capitalize,
        "MagneticFieldStrength": float,
        "InstitutionName": replace_underscores_with_spaces,
        "BodyPartExamined": str.capitalize,
        "PixelSpacing": float_list,
        "SequenceVariant": list,
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

    def to_dict(self):
        return {
            "id": f"series_{self.id}",
            "icon": "fas fa-flushed",
            "text": self.description,
        }

    def get_path(self):
        return os.path.dirname(self.instance_set.first().file.path)

    def get_default_nifti_dir(self):
        return os.path.join(os.path.dirname(self.get_path()), "NIfTI")

    def to_nifti(self, dest: str = None):
        if not self.nifti:
            dcm2nii = getattr(DjangoDicomConfig, "dcm2niix_path")
            if dcm2nii:
                if not dest:
                    dest = self.get_default_nifti_dir()
                    os.makedirs(dest, exist_ok=True)
                command = [
                    dcm2nii,
                    "-z",
                    "y",
                    "-b",
                    "n",
                    "-o",
                    dest,
                    "-f",
                    f"{self.id}",
                    self.get_path(),
                ]
                subprocess.check_output(command)
                path = os.path.join(dest, f"{self.id}.nii.gz")
                nifti_instance = NIfTI(path=path)
                nifti_instance.save()
                self.nifti = nifti_instance
                self.save()
            else:
                raise NotImplementedError(
                    "Could not call dcm2niix! Please check settings configuration."
                )
        else:
            return self.nifti

    def show(self):
        mricrogl_path = getattr(DjangoDicomConfig, "mricrogl_path")

        if self.nifti is None:
            self.to_nifti()
        with open(
            "/home/flavus/Projects/django_dicom/django_dicom/template.gls", "r"
        ) as template_file:
            template = template_file.read()

        edited = template.replace("FILE_PATH", self.nifti.path)
        with open("tmp.gls", "w") as script:
            script.write(edited)
        try:
            subprocess.check_call([mricrogl_path, "tmp.gls"])
        except subprocess.CalledProcessError:
            pass
        os.remove("tmp.gls")

    def get_instances_values(self, field_name) -> list:
        return [
            instance.headers.get(field_name)
            for instance in self.instance_set.order_by("number").all()
        ]

    def get_distinct_values(self, field_name: str) -> list:
        values = self.get_instances_values(field_name)
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

    def get_series_attribute(self, field_name: str):
        distinct = self.get_distinct_values(field_name)
        if distinct is not None and len(distinct) == 1:
            try:
                return self.ATTRIBUTE_FORMATTING[field_name](distinct.pop())
            except (TypeError, KeyError):
                return distinct.pop()
        elif distinct is not None and len(distinct) > 1:
            values = self.get_instances_values(field_name)
            try:
                return [
                    self.ATTRIBUTE_FORMATTING[field_name](value) for value in values
                ]
            except (TypeError, KeyError):
                return values
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

    class Meta:
        verbose_name_plural = "Series"
