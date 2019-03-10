import os

from django.apps import AppConfig


class DjangoDicomConfig(AppConfig):
    name = "django_dicom"
    mricrogl_path = os.getenv("MRICROGL")

    def ready(self):
        import django_dicom.signals
