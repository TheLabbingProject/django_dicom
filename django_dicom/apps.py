from django.apps import AppConfig


class DjangoDicomConfig(AppConfig):
    name = 'django_dicom'

    def ready(self):
        import django_dicom.signals
