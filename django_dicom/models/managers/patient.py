from django.db import models


class PatientManager(models.Manager):
    def get_multi_visit_patients(self) -> models.QuerySet:
        return [
            patient
            for patient in self.all()
            if patient.series_set.values_list("date", flat=True).distinct().count() > 1
        ]
