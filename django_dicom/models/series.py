import numpy as np
import os
import subprocess

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django_dicom.apps import DjangoDicomConfig
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models.nifti import NIfTI
from django_dicom.models.patient import Patient
from django_dicom.models.study import Study
from django_dicom.models.validators import digits_and_dots_only


def fix_scanning_sequence_value(value) -> list:
    if type(value) is str:
        return [value]
    else:
        return list(value)


class Series(models.Model):
    series_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series UID",
    )
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

    SPIN_ECHO = "SE"
    INVERSION_RECOVERY = "IR"
    GRADIENT_RECALLED = "GR"
    ECHO_PLANAR = "EP"
    RESEARCH_MODE = "RM"
    SCANNING_SEQUENCE_CHOICES = (
        (SPIN_ECHO, "Spin Echo"),
        (INVERSION_RECOVERY, "Inversion Recovery"),
        (ECHO_PLANAR, "Echo Planar"),
        (RESEARCH_MODE, "Research Mode"),
    )
    scanning_sequence = ChoiceArrayField(
        models.CharField(max_length=2, choices=SCANNING_SEQUENCE_CHOICES),
        size=5,
        blank=True,
        null=True,
    )

    date = models.DateField()
    time = models.TimeField()
    description = models.CharField(max_length=64)
    nifti = models.OneToOneField(
        "django_dicom.nifti", on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    study = models.ForeignKey(
        Study, blank=True, null=True, on_delete=models.PROTECT, related_name="series"
    )
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.PROTECT, related_name="series"
    )

    ATTRIBUTE_FORMATTING = {
        "InversionTime": int,
        "EchoTime": float,
        "RepetitionTime": int,
        "PixelBandwidth": int,
        "SAR": float,
        "FlipAngle": int,
        "ScanningSequence": fix_scanning_sequence_value,
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

    def get_instances_values(self, field_name):
        return {
            instance: instance.headers.get(field_name)
            for instance in self.instances.all()
        }

    def get_distinct_values(self, field_name: str):
        values = self.get_instances_values(field_name).values()
        try:
            return set(values)
        except TypeError:
            unique = []
            for value in values:
                if value not in unique:
                    unique += [value]
            return unique

    def get_series_attribute(self, field_name: str):
        values = self.get_distinct_values(field_name)
        if len(values) == 1:
            try:
                return self.ATTRIBUTE_FORMATTING[field_name](values.pop())
            except (TypeError, KeyError):
                pass
        return None

    class Meta:
        verbose_name_plural = "Series"
