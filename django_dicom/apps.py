import os
from django.apps import AppConfig


class DjangoDicomConfig(AppConfig):
    name = 'django_dicom'
    dcm2niix_path = os.getenv('DCM2NIIX')
    mricrogl_path = os.getenv('MRICROGL')

    def ready(self):
        import django_dicom.signals
