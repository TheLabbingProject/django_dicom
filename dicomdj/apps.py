from django.apps import AppConfig


class DicomDjConfig(AppConfig):
    name = 'dicomdj'

    def ready(self):
        import dicomdj.signals
