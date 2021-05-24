"""
Definition of the :class:`DjangoDicomConfig` class.
"""
import logging

from django.apps import AppConfig
from django.conf import settings
from pynetdicom import AE
from pynetdicom._globals import ALL_TRANSFER_SYNTAXES
from pynetdicom.sop_class import VerificationSOPClass

from django_dicom.utils.networking import get_application_entity_title


class DjangoDicomConfig(AppConfig):
    """
    :mod:`django_dicom`'s app configuration.
    """

    name: str = "django_dicom"
    """
    Django app name.
    """

    data_extension: str = "dcm"
    """
    File extension to validate saved files with.
    """

    application_entity: AE = None
    """
    pynetdicom application entity, used for DICOM networking.
    """

    def ready(self):
        tests_startup = getattr(settings, "TESTS", False)
        scu_autoconnect = getattr(settings, "DICOM_SCU_AUTOCONNECT", True)
        if (
            scu_autoconnect
            and not tests_startup
            and self.application_entity is None
        ):
            self.application_entity = self.create_application_entity()
            self.start_servers()

    def create_application_entity(
        self, allow_echo: bool = True, maximum_pdu_size: int = 0
    ) -> AE:
        """
        Returns an :class:`~pynetdicom.ae.ApplicationEntity` instance.

        Parameters
        ----------
        allow_echo : bool
            Whether to enable C-ECHO request handling or not, default is True
        maximum_pdu_size : int
            Maximal PDU size. By default, overrides pynetdicom's default
            setting to 0 (unlimited)

        Returns
        -------
        AE
            DICOM networking application entity
        """
        from django_dicom.models.networking import (
            messages as networking_messages,
        )

        logger = logging.getLogger("data.dicom.networking")

        ae_title = get_application_entity_title()
        start_message = networking_messages.APPLICATION_ENTITY_START.format(
            title=ae_title
        )
        logger.info(start_message)

        application_entity = AE(ae_title=ae_title)

        end_message = networking_messages.APPLICATION_ENTITY_SUCCESS
        logger.info(end_message)

        if allow_echo:
            application_entity.add_supported_context(
                VerificationSOPClass, ALL_TRANSFER_SYNTAXES[:]
            )
            logger.debug(networking_messages.C_ECHO_HANDLING)

        application_entity.maximum_pdu_size = maximum_pdu_size
        if maximum_pdu_size != 0:
            message = networking_messages.PDU_LIMIT_CONFIGURATION.format(
                maximum_pdu_size=maximum_pdu_size
            )
            logger.debug(message)

        return application_entity

    def start_servers(self):
        """
        Creates the :class:`pynetdicom.transport.ThreadedAssociationServer`
        instances to manage requests from storage service class users.

        See Also
        --------
        * :class:`~pynetdicom.transport.ThreadedAssociationServer`
        * :attr:`~pynetdicom.ae.ApplicationEntity._servers`
        * :func:`create_application_entity`
        * :attr:`application_entity`
        """
        StorageServiceClassUser = self.get_model("StorageServiceClassUser")
        StorageServiceClassUser.objects.start_servers()
