"""
Event handlers for associated service classes.
"""
from django_dicom.models.image import Image
from pydicom.filewriter import write_file_meta_info
from pynetdicom import events
from pynetdicom.status import Status


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
    with open(event.request.AffectedSOPInstanceUID, "wb") as f:
        # Write the preamble and prefix
        f.write(b"\x00" * 128)
        f.write(b"DICM")

        # Encode and write the File Meta Information
        write_file_meta_info(f, event.file_meta)

        # Write the encoded dataset
        dataset = event.request.DataSet.getvalue()
        f.write(dataset)

        # Store received data in the database
        path = Image.objects.store_image_data(f)
        Image.objects.get_or_create(dcm=path)

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
