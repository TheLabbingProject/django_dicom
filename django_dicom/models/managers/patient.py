from django.db.models import QuerySet
from django_dicom.models.managers.dicom_entity import DicomEntityManager


class PatientManager(DicomEntityManager):
    UID_FIELD = "patient_id"

    def get_multi_visit_patients(self) -> QuerySet:
        return [
            patient
            for patient in self.all()
            if patient.series_set.values_list("date", flat=True).distinct().count() > 1
        ]
