from django.db import models
from django.urls import reverse
from django_dicom.models.code_strings import Sex


class Patient(models.Model):
    patient_id = models.CharField(max_length=64, unique=True)
    given_name = models.CharField(max_length=64, blank=True)
    family_name = models.CharField(max_length=64, blank=True)
    middle_name = models.CharField(max_length=64, blank=True)
    name_prefix = models.CharField(max_length=64, blank=True)
    name_suffix = models.CharField(max_length=64, blank=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=6, choices=Sex.choices(), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    subject = models.ForeignKey(
        "research.Subject",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="mri_patient_set",
    )

    def __str__(self):
        return self.patient_id

    def get_absolute_url(self):
        return reverse("dicom:patient_detail", args=[str(self.id)])

    def get_name_id(self):
        return f"{self.family_name[:2]}{self.given_name[:2]}"

    def get_subject_attributes(self) -> dict:
        return {
            "first_name": self.given_name,
            "last_name": self.family_name,
            "date_of_birth": self.date_of_birth,
            "sex": self.sex,
            "id_number": self.patient_id,
        }

    def to_tree(self) -> list:
        return [series.to_dict() for series in self.series_set.all()]

    def get_anatomicals(self, by_date=False):
        return self.series_set.get_anatomicals(by_date)

    def get_default_anatomical(self):
        return self.series_set.get_default_anatomical()

    def get_inversion_recovery(self):
        return self.series_set.get_inversion_recovery()

    def get_latest_inversion_recovery_sequence(self):
        return self.series_set.get_latest_inversion_recovery_sequence()

    def get_anatomicals_by_pixel_spacing(self, pixel_spacing: list):
        return self.series_set.get_anatomicals_by_pixel_spacing(pixel_spacing)
