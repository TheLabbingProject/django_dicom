import numpy as np

from django.db import models
from django.urls import reverse
from django_dicom.models.patient import Patient
from django_dicom.models.study import Study
from django_dicom.models.validators import digits_and_dots_only


class Series(models.Model):
    series_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name='Series UID',
    )
    number = models.IntegerField(verbose_name='Series Number')
    date = models.DateField()
    time = models.TimeField()
    description = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    study = models.ForeignKey(
        Study, blank=True, null=True, on_delete=models.PROTECT)
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.series_uid

    def get_absolute_url(self):
        return reverse('dicom:series_detail', args=[str(self.id)])

    def get_data(self) -> np.ndarray:
        instances = self.instance_set.order_by('number')
        return np.stack(
            [instance.read_data().pixel_array for instance in instances],
            axis=-1)

    def to_dict(self):
        return {
            'id': f'series_{self.id}',
            'icon': 'fas fa-flushed',
            'text': self.description,
        }

    class Meta:
        verbose_name_plural = 'Series'
