"""
Definition of the :class:`StorageScuQuerySet` class.
"""
import logging
from typing import List

from django.db import models
from django_dicom.models.managers import messages
from pynetdicom.transport import ThreadedAssociationServer


class StorageScuQuerySet(models.QuerySet):
    """
    Custom queryset manager of the
    :class:`~django_dicom.models.networking.storage_scu.StorageServiceClassUser`
    model.
    """

    _logger = logging.getLogger("data.dicom.networking")

    def start_servers(self) -> List[ThreadedAssociationServer]:
        """
        Start association servers with all registered storage service class
        users.

        Returns
        -------
        List[ThreadedAssociationServer]
            Association servers
            """
        if not self.exists():
            return
        self._log_association_start()
        return [storage_user.associate() for storage_user in self.all()]

    def _log_association_start(self) -> None:
        """
        Logs the beginning of association requests negotation.
        """
        message = messages.SERVER_ASSOCIATION_START.format(
            n_servers=self.count()
        )
        self._logger.info(message)
