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

    status = serializers.SerializerMethodField()

    class Meta:
        model = StorageServiceClassProvider
        fields = "id", "title", "ip", "port", "status"

    def get_status(self, instance: StorageServiceClassProvider) -> str:
        """
        Returns the current association status.

        Parameters
        ----------
        instance : StorageServiceClassProvider
            Queried storage SCP instance

        Returns
        -------
        str
            Association status
        """
        return instance.status.value
