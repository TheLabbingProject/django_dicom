"""
Event handlers for associated service classes.
"""
import logging
from pathlib import Path

from django.conf import settings
from django_dicom.models.image import Image
from django_dicom.models.networking import messages
from pydicom.filewriter import write_file_meta_info
from pynetdicom import events
from pynetdicom.status import Status

logger = logging.getLogger("data.dicom.networking")

MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT"))


def handle_echo(event: events.Event) -> Status:
    """
    Optional implementation of the evt.EVT_C_ECHO handler.

    Parameters
    ----------
    event : events.Event
        Transmitted C-STORE request event

    Returns
    -------
    Status
        Response status code
    """
    logger.debug(messages.C_ECHO_RECEIVED)
    return Status.SUCCESS


def get_temp_store_path(instance_uid: str) -> Path:
    return MEDIA_ROOT / f"{instance_uid}.dcm"


def handle_store(event: events.Event) -> Status:
    """
    Handle a C-STORE request event and save dataset to the database.

    Parameters
    ----------
    event : events.Event
        Transmitted C-STORE request event

    Returns
    -------
    Status
        Response status code

    See Also
    --------
    * `Handler implementation documentation`_

    .. _Handler implementation documentation:
       https://pydicom.github.io/pynetdicom/stable/reference/generated/pynetdicom._handlers.doc_handle_store.html#pynetdicom._handlers.doc_handle_store
    """
    instance_uid = event.request.AffectedSOPInstanceUID
    path = get_temp_store_path(instance_uid)

    write_start = messages.C_STORE_RECEIVED.format(instance_uid=instance_uid)
    logging.debug(write_start)

    with open(path, "wb") as content:
        # Write the preamble and prefix
        logging.debug(messages.WRITE_DICOM_PREFIX)
        content.write(b"\x00" * 128)
        content.write(b"DICM")

        # Encode and write the File Meta Information
        logging.debug(messages.WRITE_DICOM_METADATA)
        write_file_meta_info(content, event.file_meta)

        # Write the encoded dataset
        logging.debug(messages.WRITE_DICOM_DATASET)

        dataset = event.request.DataSet.getvalue()
        content.write(dataset)

        write_end = messages.WRITE_DICOM_END.format(file_name=path.name)
        logging.debug(write_end)

    # Store received data in the database
    import_start = messages.IMAGE_IMPORT_START.format(file_name=path.name)
    logger.debug(import_start)

    Image.objects.get_or_create(dcm=path)

    import_end = messages.IMAGE_IMPORT_END.format(file_name=path.name)
    logger.debug(import_end)

    # Remove temporary file
    remove_start = messages.TEMP_DICOM_REMOVAL_START.format(
        file_name=path.name
    )
    logger.debug(remove_start)

    path.unlink()

    remove_end = messages.TEMP_DICOM_REMOVAL_END.format(file_name=path.name)
    logger.debug(remove_end)

    return Status.SUCCESS


handlers = [
    (events.EVT_C_ECHO, handle_echo),
    (events.EVT_C_STORE, handle_store),
]
"""
Default handlers specification used to intercept C-STORE and C-ECHO requests.

See Also
--------
* :func:`handle_store`
"""
