from django_dicom.models.managers.dicom_entity import DicomEntityManager


class StudyManager(DicomEntityManager):
    UID_FIELD = "study_uid"
