"""
Manages `DICOM <https://en.wikipedia.org/wiki/DICOM>`__ files by creating
`Django models <https://docs.djangoproject.com/en/2.2/topics/db/models/>`__ to
represent the various `DICOM <https://en.wikipedia.org/wiki/DICOM>`__ entities
(see :ref:`django-dicom-models` for more information). Also provides the
:ref:`django-dicom-data-import` for supervising the maintenance of these models
when importing new data, and a few more utility modules meant to help retrieving
DICOM data easily and efficiently.

"""

default_app_config = "django_dicom.apps.DjangoDicomConfig"

