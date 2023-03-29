"""
Definition of the :class:`StorageServiceClassProvider` model.
"""
import logging
from typing import List

from django.apps import apps
from django.core.validators import MaxValueValidator
from django.db import models
from django_dicom.models.managers.storage_scp import StorageScpQuerySet
from django_dicom.models.networking import messages
from django_dicom.models.networking.handlers import handlers
from django_dicom.models.networking.status import ServerStatus
from django_dicom.models.networking.utils import (
    MAX_PORT_NUMBER,
    PRESENTATION_CONTEXTS,
    UID_MAX_LENGTH,
)
from django_dicom.models.utils.fields import ChoiceArrayField
from pynetdicom import AE, AllStoragePresentationContexts
from pynetdicom.presentation import PresentationContext
from pynetdicom.transport import ThreadedAssociationServer


class StorageServiceClassProvider(models.Model):
    """
    Storage Service Class Provider (SCP) to handle C-STORE requests.
    """

    title = models.CharField(max_length=128, blank=True, null=True)
    """
    Optional title for this storage service provider.
    """

    ip = models.GenericIPAddressField(verbose_name="IP", blank=True, null=True)
    """
    Storage service provider's IP address.
    """

    port = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_PORT_NUMBER)], default=11112
    )
    """
    Associated storage service provider's port.
    """

    supported_contexts = ChoiceArrayField(
        models.CharField(
            max_length=UID_MAX_LENGTH,
            choices=PRESENTATION_CONTEXTS,
            blank=False,
            null=False,
        ),
        blank=False,
        null=False,
    )
    """
    Supported presentation contexts.
    """

    objects = StorageScpQuerySet.as_manager()
    """
    Custom manager class.

    See Also
    --------
    * :class:`~django_dicom.models.managers.storage_scp.StorageScpQuerySet`
    * :func:`django.db.models.QuerySet.as_manager`
    """

    _logger = logging.getLogger("data.dicom.networking")

    class Meta:
        verbose_name = "Storage SCP"

    def __str__(self) -> str:
        """
        Returns the string representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """
        ip = self.ip or "0.0.0.0"
        return f"{self.title}@{ip}:{self.port}"

    def get_application_entity(self) -> AE:
        """
        Returns the app's active application entity instance.

        Returns
        -------
        AE
            Active application entity

        See Also
        --------
        * :attr:`application_entity`
        """
        config = apps.get_app_config("django_dicom")
        return config.application_entity

    def start(self) -> ThreadedAssociationServer:
        """
        Start an association server with this provider to listen for requests.

        Returns
        -------
        ThreadedAssociationServer
            Non-blocking association server
        """
        self._log_server_start()
        ip = self.ip or ""
        if self.server is not None:
            return self.server
        try:
            server = self.application_entity.start_server(
                (ip, self.port),
                block=False,
                evt_handlers=handlers,
                contexts=self._supported_contexts,
            )
        except (ValueError, OSError) as exception:
            self._log_server_start_error(exception)
        else:
            if isinstance(server, ThreadedAssociationServer):
                self._log_server_start_success()
                return server
            else:
                self._log_silent_failure()

    def _log_server_start(self) -> None:
        """
        Logs the beginning of an association request with storage service class
        provider.
        """
        message = messages.SERVER_START.format(provider=str(self))
        self._logger.info(message)

    def _log_server_start_success(self) -> None:
        """
        Logs the end of a successful association request with storage service
        class provider.
        """
        self._logger.info(messages.SERVER_START_SUCCESS)

    def _log_server_start_error(self, exception: ValueError) -> None:
        """
        Logs ValueErrors raised by
        :func:`~pynetdicom.ae.ApplicationEntity.start_server`.

        Parameters
        ----------
        exception : ValueError
            Raised exception
        """
        message = messages.SERVER_START_ERROR.format(exception=exception)
        self._logger.warning(message)

    def _log_silent_failure(self) -> None:
        """
        Logs the case where no exception was raised but the association server
        could not be found under the app's application entity.
        """
        self._logger.warning(messages.SERVER_NOT_CREATED)

    def get_server(self) -> ThreadedAssociationServer:
        """
        Returns the association server instance.

        Returns
        -------
        ThreadedAssociationServer
            DICOM storage SCP threaded association server

        See Also
        --------
        * :attr:`server`
        """
        servers = self.application_entity._servers
        ip = self.ip or "0.0.0.0"
        server_address = ip, self.port
        try:
            return [
                server for server in servers if server.server_address == server_address
            ][0]
        except IndexError:
            pass

    @property
    def _supported_contexts(self) -> List[PresentationContext]:
        """
        Supported presentation contexts to specify on association negotation.

        Returns
        -------
        List[PresentationContext]
            Accepted presentation contexts

        See Also
        --------
        * :func:`associate`
        """
        return [
            context
            for context in AllStoragePresentationContexts
            if str(context.abstract_syntax) in self.supported_contexts
        ]

    @property
    def application_entity(self) -> AE:
        """
        Returns the app's active application entity instance.

        Returns
        -------
        AE
            Active application entity

        See Also
        --------
        * :func:`get_application_entity`
        """
        return self.get_application_entity()

    def check_status(self) -> ServerStatus:
        """
        Returns the association status.

        Returns
        -------
        ServerStatus
            Server association status

        See Also
        --------
        :func:`is_down`
        :func:`is_up`
        """
        if self.server is None:
            return ServerStatus.DOWN
        up = bool(self.server.active_associations)
        return ServerStatus.UP if up else ServerStatus.INACTIVE

    @property
    def server(self) -> ThreadedAssociationServer:
        """
        Returns the association server instance.

        Returns
        -------
        ThreadedAssociationServer
            DICOM storage SCP threaded association server

        See Also
        --------
        * :attr:`get_server`
        """
        return self.get_server()

    @property
    def status(self) -> ServerStatus:
        """
        Returns the association status.

        Returns
        -------
        ServerStatus
            Server association status

        See Also
        --------
        :func:`check_status`
        """
        return self.check_status()

    @property
    def is_down(self) -> bool:
        """
        Returns whether the association with storage SCP is down or not.

        Returns
        -------
        bool
            Whether the association is down or not

        See Also
        --------
        :func:`check_status`
        :func:`is_up`
        :attr:`~pynetdicom.transport.ThreadedAssociationServer.active_associations`
        """
        return

    @property
    def is_up(self) -> bool:
        """
        Returns whether the association with storage SCP is up or not.

        Returns
        -------
        bool
            Whether the association is up or not

        See Also
        --------
        :func:`check_status`
        :func:`is_down`
        """
        return self.server is not None and len(self.server.active_associations) == 0
