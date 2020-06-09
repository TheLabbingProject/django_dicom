Import Modes
============

Currently, three import modes are available:

    - Minimal: Do not create :class:`~django_dicom.models.header.Header`
      or :class:`~django_dicom.models.data_element.DataElement` instances
      at all.
    - Normal: Create :class:`~django_dicom.models.header.Header`\s and save
      only `standard data elements`_ to the database.
    - Full: Create :class:`~django_dicom.models.header.Header`\s and save
      all data elements to the database.

By default, *django_dicom*'s import mode will be set to ``Normal``.

.. _standard data elements:
   https://nipy.org/nibabel/dicom/dicom_intro.html#private-attribute-tags

Changing Import Mode
--------------------

In order to change the import mode, in your `project settings`_ add:

.. code-block:: python

    DICOM_IMPORT_MODE = "minimal" # or "full"


.. _project settings: https://docs.djangoproject.com/en/3.0/ref/settings/