from django_dicom.models.patient import Patient
from django_dicom.models.series import Series
from django_dicom.models.study import Study
from rest_framework import serializers


class SeriesSerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for the :class:`~django_dicom.models.series.Series` model.
    
    """

    url = serializers.HyperlinkedIdentityField(view_name="dicom:series-detail")
    study = serializers.HyperlinkedRelatedField(
        view_name="dicom:study-detail", queryset=Study.objects.all()
    )
    patient = serializers.HyperlinkedRelatedField(
        view_name="dicom:patient-detail", queryset=Patient.objects.all()
    )

    class Meta:
        model = Series
        fields = (
            "id",
            "url",
            "study",
            "patient",
            "body_part_examined",
            "patient_position",
            "number",
            "description",
            "date",
            "time",
            "modality",
            "protocol_name",
            "scanning_sequence",
            "sequence_variant",
            "pixel_spacing",
            "slice_thickness",
            "echo_time",
            "inversion_time",
            "repetition_time",
            "flip_angle",
            "manufacturer",
            "manufacturer_model_name",
            "magnetic_field_strength",
            "device_serial_number",
            "institution_name",
            "uid",
        )
