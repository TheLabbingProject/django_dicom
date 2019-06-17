from django.apps import apps
from django.conf import settings
from django_dicom.models.patient import Patient
from rest_framework import serializers

if hasattr(settings, "SUBJECT_MODEL"):
    subject_app_label, subject_model_name = settings.SUBJECT_MODEL.split(".")
    subject_view = f"{subject_app_label}:{subject_model_name.lower()}-detail"
    Subject = apps.get_model(app_label=subject_app_label, model_name=subject_model_name)


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for the :class:`~django_dicom.models.patient.Patient` model.
    
    """

    if hasattr(settings, "SUBJECT_MODEL"):
        subject = serializers.HyperlinkedRelatedField(
            view_name=subject_view, queryset=Subject.objects.all(), allow_null=True
        )

    class Meta:
        model = Patient
        fields = (
            "id",
            "uid",
            "name_prefix",
            "given_name",
            "middle_name",
            "family_name",
            "name_suffix",
            "sex",
            "date_of_birth",
            "subject",
        )

