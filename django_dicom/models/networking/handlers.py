"""
Event handlers for associated service classes.
"""
import logging

from django_dicom.models.networking import messages
from django_dicom.models.networking.logging import log_c_store_received
from django_dicom.models.networking.utils import import_dataset_to_db
from pynetdicom import events
from pynetdicom.status import Status

logger = logging.getLogger("data.dicom.networking")


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
    log_c_store_received()
    import_dataset_to_db(event)
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
