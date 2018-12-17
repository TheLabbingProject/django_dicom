import os
from django.apps import AppConfig


class DjangoDicomConfig(AppConfig):
    name = 'django_dicom'
    dcm2niix_path = os.environ['DCM2NIIX']
    mricrogl_path = os.environ['MRICROGL']

    def ready(self):
        import django_dicom.signals
