"""
Definition of the :class:`DjangoDicomConfig` class.
"""

from django.apps import AppConfig
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
        # Create application entity.
        ae_title = get_application_entity_title()
        self.application_entity = AE(ae_title=ae_title)

        # Enable C-ECHO request handling.
        self.application_entity.add_supported_context(
            VerificationSOPClass, ALL_TRANSFER_SYNTAXES[:]
        )

        # Set unlimited PDU size to maximize throughput.
        self.application_entity.maximum_pdu_size = 0

        # Associate the created application entity with any registered users.
        StorageUser = self.get_model("StorageServiceClassUser")
        for user in StorageUser.objects.all():
            if user.server is None:
                user.start()
