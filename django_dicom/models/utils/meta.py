from django.apps import apps
from django.db.models import Model


APP_LABEL = "django_dicom"


def get_model(model_name: str) -> Model:
    return apps.get_model(APP_LABEL, model_name=model_name)
