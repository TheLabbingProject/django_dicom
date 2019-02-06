from django.db import models
from django.urls import reverse
from django_dicom.models.choices import Sex


class Patient(models.Model):
    patient_id = models.CharField(max_length=64, unique=True)
    given_name = models.CharField(max_length=64, blank=True)
    family_name = models.CharField(max_length=64, blank=True)
    middle_name = models.CharField(max_length=64, blank=True)
    name_prefix = models.CharField(max_length=64, blank=True)
    name_suffix = models.CharField(max_length=64, blank=True)
    date_of_birth = models.DateField()
    sex = models.CharField(
        max_length=6,
        choices=Sex.choices(),
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    subject = models.ForeignKey(
        'research.Subject',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='mri')

    def __str__(self):
        return self.patient_id

    def get_absolute_url(self):
        return reverse('dicom:patient_detail', args=[str(self.id)])

    def get_name_id(self):
        return f'{self.family_name[:2]}{self.given_name[:2]}'

    def get_subject_attributes(self) -> dict:
        return {
            'first_name': self.given_name,
            'last_name': self.family_name,
            'date_of_birth': self.date_of_birth,
            'sex': self.sex,
            'id_number': self.patient_id,
        }

    def to_tree(self) -> list:
        return [series.to_dict() for series in self.series_set.all()]
