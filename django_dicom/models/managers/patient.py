from django_dicom.models.managers.dicom_entity import DicomEntityManager


class PatientManager(DicomEntityManager):
    UID_FIELD = "patient_id"
