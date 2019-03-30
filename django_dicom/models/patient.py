import numpy as np

from django.db import models
from django.urls import reverse
from django_dicom.models import Instance
from django_dicom.models.code_strings import Sex
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers import PatientManager


class Patient(DicomEntity):
    patient_id = models.CharField(max_length=64, unique=True)
    given_name = models.CharField(max_length=64, blank=True, null=True)
    family_name = models.CharField(max_length=64, blank=True, null=True)
    middle_name = models.CharField(max_length=64, blank=True, null=True)
    name_prefix = models.CharField(max_length=64, blank=True, null=True)
    name_suffix = models.CharField(max_length=64, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=6, choices=Sex.choices(), blank=True, null=True)
    comments = models.TextField(max_length=1000, blank=True, null=True)
    is_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    subject = models.ForeignKey(
        "research.Subject",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="mri_patient_set",
    )

    objects = PatientManager()

    FIELD_TO_HEADER = {
        "patient_id": "PatientID",
        "date_of_birth": "PatientBirthDate",
        "sex": "PatientSex",
    }
    NAME_PARTS = [
        "given_name",
        "family_name",
        "middle_name",
        "name_prefix",
        "name_suffix",
    ]

    def __str__(self) -> str:
        return self.patient_id

    def get_absolute_url(self):
        return reverse("dicom:patient_detail", args=[str(self.id)])

    def get_full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"

    def get_name_id(self) -> str:
        return f"{self.family_name[:2]}{self.given_name[:2]}"

    def get_latest_instance(self):
        return self.instance_set.order_by("-created_at").first()

    def get_latest_header_value(self, tag_or_keyword):
        latest_instance = self.get_latest_instance()
        if latest_instance:
            return latest_instance.get_header_value(tag_or_keyword)
        return None

    def update_patient_name(self, force=False) -> bool:
        latest = self.get_latest_header_value("PatientName")
        for part in self.NAME_PARTS:
            not_null = getattr(self, part, False)
            if not force and not_null:
                continue
            value = getattr(latest, part, None)
            if value:
                setattr(self, part, value)

    def update_fields_from_header(self, force=False):
        for field in self.get_model_header_fields():
            if not force and getattr(self, field.name, False):
                continue
            header_name = self.FIELD_TO_HEADER.get(field.name)
            if header_name:
                latest_value = self.get_latest_header_value(header_name)
                if latest_value:
                    setattr(self, field.name, latest_value)
        self.update_patient_name(force=force)
        self.is_updated = True

    def to_tree(self) -> list:
        return [series.to_tree_node() for series in self.series_set.all()]

    def get_anatomicals(self, by_date: bool = False):
        return self.series_set.get_anatomicals(by_date=by_date)

    def get_default_anatomical(self):
        return self.series_set.get_default_anatomical()

    def get_second_session_anatomical(self):
        anatomicals_by_date = self.series_set.get_anatomicals(by_date=True)
        if len(anatomicals_by_date) > 1:
            default = self.get_default_anatomical()
            del anatomicals_by_date[default.date]
            return (
                list(anatomicals_by_date.values())[0]
                .order_by("pixel_spacing__0", "pixel_spacing__1")
                .first()
            )

    def get_inversion_recovery(self):
        return self.series_set.get_inversion_recovery()

    def get_latest_inversion_recovery_sequence(self):
        return self.series_set.get_latest_inversion_recovery_sequence()

    def get_anatomicals_by_pixel_spacing(self, pixel_spacing: list):
        return self.series_set.get_anatomicals_by_pixel_spacing(pixel_spacing)

    def calculate_mutual_information(
        self, other, histogram_bins: int = 10
    ) -> np.float64:
        self_anatomical = self.get_default_anatomical()
        other_anatomical = other.get_default_anatomical()
        return self_anatomical.calculate_mutual_information(
            other_anatomical, histogram_bins
        )

    class Meta:
        indexes = [
            models.Index(fields=["patient_id"]),
            models.Index(fields=["date_of_birth"]),
        ]

    @property
    def has_series(self):
        return bool(self.series_set.count())

    @property
    def instance_set(self):
        return Instance.objects.filter(series__in=self.series_set.all())

