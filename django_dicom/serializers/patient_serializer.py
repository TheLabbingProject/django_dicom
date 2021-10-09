"""
Definition of the :class:`PatientSerializer` class.
"""
from django_dicom.models.patient import Patient
from rest_framework import serializers


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer class for the
    :class:`~django_dicom.models.patient.Patient` model.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="dicom:patient-detail"
    )
    n_studies = serializers.IntegerField(
        read_only=True,
        label="Study Count",
        help_text="The number of studies associated with this patient.",
    )
    n_series = serializers.IntegerField(
        read_only=True,
        label="Series Count",
        help_text="The number of series associated with this patient.",
    )
    n_images = serializers.IntegerField(
        read_only=True,
        label="Image Count",
        help_text="The number of images associated with this patient.",
    )

    class Meta:
        model = Patient
        fields = (
            "id",
            "url",
            "uid",
            "name_prefix",
            "given_name",
            "middle_name",
            "family_name",
            "name_suffix",
            "sex",
            "date_of_birth",
            "n_studies",
            "n_series",
            "n_images",
        )
