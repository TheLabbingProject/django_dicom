from django_dicom.models.networking import StorageServiceClassUser
from rest_framework import serializers


class StorageScuSerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer
    <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for
    the
    :class:`~django_dicom.models.networking.storage_scu.StorageServiceClassUser`
    model.
    """

    class Meta:
        model = StorageServiceClassUser
        fields = "id", "title", "ip", "port"
