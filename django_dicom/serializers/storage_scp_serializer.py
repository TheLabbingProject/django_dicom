"""
Definition of the :class:`StorageScpSerializer` class.
"""
from django_dicom.models.networking import StorageServiceClassProvider
from rest_framework import serializers


class StorageScpSerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer class for the
    :class:`~django_dicom.models.networking.storage_scp.StorageServiceClassProvider`
    model.
    """

    class Meta:
        model = StorageServiceClassProvider
        fields = "id", "title", "ip", "port"
