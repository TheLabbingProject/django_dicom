"""
Definition of the :class:`StorageServiceClassUser` model.
"""
import logging
from typing import List

from django.apps import apps
from django.core.validators import MaxValueValidator
from django.db import models
from django_dicom.models.managers.storage_scu import StorageScuQuerySet
from django_dicom.models.networking import messages
from django_dicom.models.networking.handlers import handlers
from django_dicom.models.networking.utils import (
    MAX_PORT_NUMBER,
    PRESENTATION_CONTEXTS,
    UID_MAX_LENGTH,
)
from django_dicom.models.utils.fields import ChoiceArrayField
from pynetdicom import AE, AllStoragePresentationContexts
from pynetdicom.presentation import PresentationContext
from pynetdicom.transport import ThreadedAssociationServer


class StorageServiceClassUser(models.Model):
    """
    Storage Service Class User (SCU) to accept C-STORE events from.
    """

    title = models.CharField(max_length=128, blank=True, null=True)
    """
    Optional title for this storage service user.
    """

    ip = models.GenericIPAddressField(verbose_name="IP")
    """
    Associated storage service user's IP address.
    """

    port = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_PORT_NUMBER)]
    )
    """
    Associated storage service user's port.
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

    objects = StorageScuQuerySet.as_manager()
    """
    Custom manager class.

    See Also
    --------
    * :class:`~django_dicom.models.managers.storage_scu.StorageScuQuerySet`
    * :func:`django.db.models.QuerySet.as_manager`
    """

    server: ThreadedAssociationServer = None
    """
    The association server for this user. Should be overridden on application
    startup by the :func:`associate` method.
    """

    _logger = logging.getLogger("data.dicom.networking")

    class Meta:
        verbose_name = "Storage SCU"

    def __str__(self) -> str:
        """
        Returns the string representation of this instance.

        Returns
        -------
        str
            This instance's string representation
        """
        return f"{self.title}@{self.ip}:{self.port}"

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

    def associate(self) -> ThreadedAssociationServer:
        """
        Start an association server with this user to listen for requests.

        Returns
        -------
        ThreadedAssociationServer
            Non-blocking association server
        """
        self._log_association_start()
        n_servers_before = len(self.application_entity._servers)
        try:
            self.server = self.application_entity.start_server(
                (self.ip, self.port),
                block=False,
                evt_handlers=handlers,
                contexts=self._supported_contexts,
            )
        except ValueError as exception:
            self._log_association_valueerror(exception)
        else:
            n_servers_after = len(self.application_entity._servers)
            if n_servers_after == n_servers_before + 1:
                self._log_association_success()
                return self.server
            else:
                self._log_silent_failure()

    def _log_association_start(self) -> None:
        """
        Logs the beginning of an association request with storage service class
        user.
        """
        message = messages.SERVER_ASSOCIATION_START.format(user=str(self))
        self._logger.info(message)

    def _log_association_success(self) -> None:
        """
        Logs the end of a successful association request with storage service
        class user.
        """
        message = messages.SERVER_ASSOCIATION_SUCCESS.format(user=str(self))
        self._logger.info(message)

    def _log_association_valueerror(self, exception: ValueError) -> None:
        """
        Logs ValueErrors raised by
        :func:`~pynetdicom.ae.ApplicationEntity.start_server`.

        Parameters
        ----------
        exception : ValueError
            Raised exception
        """
        message = messages.SERVER_VALUE_ERROR.format(exception=exception)
        self._logger.warning(message)

    def _log_silent_failure(self) -> None:
        """
        Logs the case where no exception was raised but the association server
        could not be found under the app's application entity.
        """
        self._logger.warning(messages.SERVER_NOT_CREATED)

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
