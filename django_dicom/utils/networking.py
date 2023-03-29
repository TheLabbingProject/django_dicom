"""
General DICOM Networking utilities.
"""

from django.conf import settings

TITLE_MAX_LENGTH = 16
"""
Maximal application entity title length is limited to 16 characters.

See Also
--------
* `validate_ae_title`_

.. _validate_ae_title:
   https://github.com/pydicom/pynetdicom/blob/151e9cdff24c8b69ec485b015d93f46c54141aad/pynetdicom/utils.py#L67
"""

APPLICATION_ENTITY_TITLE_SETTING = "APPLICATION_ENTITY_TITLE"
"""
Django settings key used to specify a custom application entity title.
"""

DEFAULT_APPLICATION_ENTITY_TITLE = "DJANGO-DICOM"
"""
Default application entity title to use if none is set in Django's settings.
"""


def get_application_entity_title() -> str:
    """
    Returns the application entity title used for DICOM networking.

    Returns
    -------
    str
        Application entity title
    """
    return getattr(
        settings, APPLICATION_ENTITY_TITLE_SETTING, DEFAULT_APPLICATION_ENTITY_TITLE,
    )
