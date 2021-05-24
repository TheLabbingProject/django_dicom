"""
Definition of the :class:`StorageScpQuerySet` class.
"""
import logging
from typing import List

from django.db import models
from django_dicom.models.managers import messages
from pynetdicom.transport import ThreadedAssociationServer


class StorageScpQuerySet(models.QuerySet):
    """
    Custom queryset manager of the
    :class:`~django_dicom.models.networking.storage_scp.StorageServiceClassProvider`
    model.
    """

    _logger = logging.getLogger("data.dicom.networking")

    def start_servers(self) -> List[ThreadedAssociationServer]:
        """
        Start association servers.

        Returns
        -------
        List[ThreadedAssociationServer]
            Association servers
        """
        if not self.exists():
            return
        self._log_servers_start()
        associations = [
            storage_provider.start() for storage_provider in self.all()
        ]
        return list(filter(None, associations))

    def _log_servers_start(self) -> None:
        """
        Logs the beginning of association requests negotation.
        """
        message = messages.SERVER_START.format(n_servers=self.count())
        self._logger.info(message)
