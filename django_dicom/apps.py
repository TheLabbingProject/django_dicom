import os

from django.apps import AppConfig
from django.db.models import Q


class DjangoDicomConfig(AppConfig):
    name = 'django_dicom'
    dcm2niix_path = os.getenv('DCM2NIIX')
    mricrogl_path = os.getenv('MRICROGL')
    anatomical_flags = ['MPRAGE', 'T1w']
    ir_flags = ['IR-EPI']

    def ready(self):
        import django_dicom.signals

    @classmethod
    def anatomical_query(cls):
        query = Q()
        for flag in cls.anatomical_flags:
            query |= Q(description__icontains=flag)
        return query

    @classmethod
    def inversion_recovery_query(cls):
        query = Q()
        for flag in cls.ir_flags:
            query |= Q(description__icontains=flag)
        return query
