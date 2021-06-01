"""
Event handlers for associated service classes.
"""
import logging
from pathlib import Path

from django_dicom.models.image import Image
from django_dicom.models.networking import messages
from django_dicom.models.utils import get_dicom_root
from pydicom.filewriter import write_file_meta_info
from pynetdicom import events
from pynetdicom.status import Status

logger = logging.getLogger("data.dicom.networking")

DICOM_ROOT = get_dicom_root()
TEMP_DICOM_FILE_TEMPLATE = "{instance_uid}.dcm"


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


def get_temp_path(instance_uid: str) -> Path:
    """
    Returns a temporary path within MEDIA_ROOT to save the dataset in.

    Parameters
    ----------
    instance_uid : str
        SOP Class Instance UID

    Returns
    -------
    Path
        Temporary file path to import the dataset to the database from
    """
    file_name = TEMP_DICOM_FILE_TEMPLATE.format(instance_uid=instance_uid)
    return DICOM_ROOT / file_name


def log_c_store_received(level=logging.DEBUG) -> None:
    message = messages.C_STORE_RECEIVED
    logging.log(level, message)


def log_dataset_saved(file_name: str, level=logging.DEBUG) -> None:
    message = messages.WRITE_DICOM_END.format(file_name=file_name)
    logging.log(level, message)


def log_import_start(file_name: str, level=logging.DEBUG) -> None:
    message = messages.IMAGE_IMPORT_START.format(file_name=file_name)
    logger.log(level, message)


def log_import_end(file_name: str, level=logging.DEBUG) -> None:
    message = messages.IMAGE_IMPORT_END.format(file_name=file_name)
    logger.log(level, message)


def log_cleanup_start(file_name: str, level=logging.DEBUG) -> None:
    message = messages.TEMP_DICOM_REMOVAL_START.format(file_name=file_name)
    logger.log(level, message)


def log_cleanup_end(file_name: str, level=logging.DEBUG) -> None:
    message = messages.TEMP_DICOM_REMOVAL_END.format(file_name=file_name)
    logger.log(level, message)


def save_dataset(event: events.Event) -> Path:
    """
    Save the dataset to a temporary location within MEDIA_ROOT.

    Parameters
    ----------
    event : events.Event
        C-STORE request event
    path : Path
        Destination path
    """
    instance_uid = event.request.AffectedSOPInstanceUID
    path = get_temp_path(instance_uid)
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
    log_dataset_saved(path.name)
    return path


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
    # Save dataset to temporary location
    log_c_store_received()
    path = save_dataset(event)

    # Import dataset to the database
    log_import_start(path.name)
    Image.objects.get_or_create(dcm=path)
    log_import_end(path.name)

    # Remove temporary file
    log_cleanup_start(path.name)
    path.unlink()
    log_cleanup_end(path.name)

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
