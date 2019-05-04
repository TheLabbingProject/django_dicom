from django_dicom.models.patient import Patient
from rest_framework import serializers


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for the :class:`~django_dicom.models.patient.Patient` model.
    
    """

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
        )

