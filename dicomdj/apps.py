from django.apps import AppConfig


class DicomConfig(AppConfig):
    name = 'dicomdj'

    def ready(self):
        import dicomdj.signals
