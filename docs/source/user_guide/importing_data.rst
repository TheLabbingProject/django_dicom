Importing Data
--------------

To import a local repository of *.dcm* files, use the
:class:`~django_dicom.models.managers.image.ImageManager`\'s
:meth:`~django_dicom.models.managers.image.ImageManager.import_path` method:

.. code-block:: python

    >>> from django_dicom.models import Image

    >>> path = '/path/to/local/dcm/repo/'
    >>> results = Image.objects.import_path(path)
    Importing DICOM data: 4312image [34:24,  2.09image/s]
    Successfully imported DICOM data from '/path/to/local/dcm/repo/'!
    Created:        4312

    >>> results
    {'created': 4312, 'existing': 0}

You can verify the addition of new data to the database by querying the desired DICOM_ entity::

    >>> from django_dicom.models import Image, Patient

    >>> Image.objects.count()
    4312
    >>> Patient.objects.count()
    3



.. _DICOM: https://en.wikipedia.org/wiki/DICOM
