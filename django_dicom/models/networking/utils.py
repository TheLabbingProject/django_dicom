"""
Utilities for the networking module.
"""
import logging
from pathlib import Path

from django_dicom.models.image import Image
from django_dicom.models.networking import messages
from django_dicom.models.networking.logging import (
    log_cleanup_end,
    log_cleanup_start,
    log_dataset_saved,
    log_import_end,
    log_import_start,
)
from django_dicom.models.utils import get_dicom_root
from pydicom.filewriter import write_file_meta_info
from pynetdicom import AllStoragePresentationContexts, events

MAX_PORT_NUMBER = 65535
"""
Maximal possible port number.
"""

UID_MAX_LENGTH = 64
"""
Maximal presentation context UID length.
"""

PRESENTATION_CONTEXTS = sorted(
    [
        (str(context.abstract_syntax), context.abstract_syntax.name)
        for context in AllStoragePresentationContexts
    ],
    key=lambda choice: choice[1],
)
"""
Tuples of presentation context UIDs and string representations.
"""

TEMP_DICOM_FILE_TEMPLATE = "{instance_uid}.dcm"
"""
File name template to use when creating temporary *.dcm* files to import to
the database (used on C-STORE requests).
"""

DICOM_ROOT = get_dicom_root()
"""
DICOM data root directory with MEDIA_ROOT. Used to store the temporary *.dcm*
files created on C-STORE requests.
"""


def get_temp_path(instance_uid: str) -> Path:
    """
    Returns a temporary path within MEDIA_ROOT to save a dataset in.

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


def cleanup_temp_dcm(path: Path) -> None:
    """
    Delete the temporary *.dcm* file created within DICOM_ROOT for database
    import.

    Parameters
    ----------
    path : Path
        Temporary *.dcm* file path
    """
    log_cleanup_start(path.name)
    path.unlink()
    log_cleanup_end(path.name)


def import_dataset_to_db(event: events.Event) -> None:
    """
    Save a C-STORE request provided dataset and import to the database.

    Parameters
    ----------
    event : events.Event
        C-STORE request event
    """
    path = save_dataset(event)
    log_import_start(path.name)
    Image.objects.get_or_create(dcm=path)
    log_import_end(path.name)
    cleanup_temp_dcm(path)
