"""
Definition of the :class:`StudySerializer` class.
"""
# from django_dicom.models.image import Image
from django_dicom.models.study import Study
from rest_framework import serializers


class StudySerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer class for the :class:`~django_dicom.models.study.Study` model.
    """

    url = serializers.HyperlinkedIdentityField(view_name="dicom:study-detail")
    n_patients = serializers.IntegerField(
        read_only=True,
        label="Patient Count",
        help_text="The number of patients associated with this study.",
    )
    n_series = serializers.IntegerField(
        read_only=True,
        label="Series Count",
        help_text="The number of series associated with this study.",
    )
    n_images = serializers.IntegerField(
        read_only=True,
        label="Image Count",
        help_text="The number of images associated with this study.",
    )

    class Meta:
        model = Study
        fields = (
            "id",
            "description",
            "date",
            "time",
            "uid",
            "url",
            "n_patients",
            "n_series",
            "n_images",
        )
