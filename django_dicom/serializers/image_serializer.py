"""
Definition of the :class:`ImageSerializer` class.
"""
from django_dicom.models.image import Image
from django_dicom.models.series import Series
from rest_framework import serializers


class ImageSerializer(serializers.ModelSerializer):
    """
    A serializer class for the :class:`~django_dicom.models.image.Image` model.
    """

    series = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all())

    class Meta:
        model = Image
        fields = "id", "series", "number", "date", "time", "uid"
