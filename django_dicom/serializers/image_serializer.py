from django_dicom.models.image import Image
from django_dicom.models.series import Series
from rest_framework import serializers


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for the :class:`~django_dicom.models.image.Image` model.
    
    """

    series = serializers.HyperlinkedRelatedField(
        view_name="dicom:series-detail", queryset=Series.objects.all()
    )

    class Meta:
        model = Image
        fields = ("id", "series", "number", "date", "time", "uid")
