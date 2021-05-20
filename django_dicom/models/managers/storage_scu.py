"""
Definition of the :class:`StorageScuQuerySet` class.
"""
from typing import List

from django.db import models
from pynetdicom.transport import ThreadedAssociationServer


class StorageScuQuerySet(models.QuerySet):
    """
    Custom queryset manager of the
    :class:`~django_dicom.models.networking.storage_scu.StorageServiceClassUser`
    model.
    """

    def start_servers(self) -> List[ThreadedAssociationServer]:
        """
        Start association servers with all registered storage service class
        users.

        Returns
        -------
        List[ThreadedAssociationServer]
            Association servers
        """
        return [storage_user.associate() for storage_user in self.all()]
