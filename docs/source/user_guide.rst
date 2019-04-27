User Guide
==========

Once `django_dicom` is properly `installed <installation.html>`_ and `integrated <quickstart.html>`_
into your `Django <https://www.djangoproject.com/>`_ `project <https://docs.djangoproject.com/en/2.2/ref/applications/>`_,
enter your project's shell by running from within your project's `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_::

    python manage.py shell


Importing Data
--------------

Currently, `django_dicom` only provides methods to import data from a local repository. In general, `django_dicom` uses its
:class:`~django_dicom.data_import.import_image.ImportImage` class in order to read imported DICOM_ images and supervise
their addition to the database. 

Importing a Local DICOM_ repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To import DICOM_ images and `ZIP archives`_ containing DICOM_ images
from a directory tree found under a */path/to/repository/* base directory, simply use the 
:class:`~django_dicom.data_import.local_import.LocalImport` class::

    from django_dicom.data_import import LocalImport

    path = "/path/to/repository/"
    LocalImport(path).run()
    
This should produce output similar to this:

.. image:: images/local_import.png
    :align: center
    :alt: Image could not be retrieved!

We can see that :class:`~django_dicom.data_import.local_import.LocalImport`'s
:meth:`~django_dicom.data_import.local_import.LocalImport.run` method first imports any
files with the *dcm* extension under the base directory, and then inspects any `ZIP archives`_
found under it. :class:`~django_dicom.data_import.local_import.LocalImport` generates
the paths of files using its :meth:`~django_dicom.data_import.local_import.LocalImport.path_generator`
method, and imports the images using the :meth:`~django_dicom.data_import.local_import.LocalImport.import_local_dcm`
and :meth:`~django_dicom.data_import.local_import.LocalImport.import_local_zip_archive`
`class methods <https://www.geeksforgeeks.org/class-method-vs-static-method-python/>`_.

.. note::
    The :meth:`~django_dicom.data_import.local_import.LocalImport.run` method can easily be configured
    to run without the streamed output using ``verbose=False``. 

.. note::
    You can also skip ZIP archive import with ``import_zip=False``.
    This is equivalent to running::
 
        LocalImport(path).import_local_dcms()
        # == LocalImport(path).run(import_zip=False)
    
    For more information see :class:`~django_dicom.data_import.local_import.LocalImport`.

You can verify the addition of new data to the database by querying the desired DICOM_ entity::

    from django_dicom.models import Image, Patient

    Image.objects.count()
    # Out: 1083
    Patient.objects.count()
    # Out: 3


Reading Header Information
--------------------------

DICOM_ images have a lot of infomation stored in `header tags <https://www.dicomlibrary.com/dicom/dicom-tags/>`_.
`django_dicom` includes a :mod:`~django_dicom.reader` module that includes both a :class:`~django_dicom.reader.header_information.HeaderInformation` class
to provide easy interaction with the header data, and a :class:`~django_dicom.reader.parser.DicomParser` class that handles parsing of DICOM_ `data elements <https://www.dicomlibrary.com/dicom/dicom-tags/>`_
into native python types. 

We can easily query header fields using either their name or their tag through an :class:`~django_dicom.models.image.Image` instance's :attr:`~django_dicom.models.image.Image.header` property::

    from django_dicom.models import Image

    image = Image.objects.last()
    
    # Querying using the DICOM attribute name:
    image.header.get_value("InstanceCreationTime")
    # Out: datetime.time(12, 44, 46, 263000)

    # Querying the Patient's Age attribute using its DICOM tag:
    image.header.get_value(("0010", "1010"))
    # Out: 27.0
    # (the parser automatically returns the age as a float representing whole years)




Reading Image Data
------------------

Let's query one of the anatomical series we've added. We know their `Series Description`_ DICOM_
header attribute should contain the acronym "MPRAGE"[#0]_, so one easy way for querying such a series would be::

    from django_dicom.models import Series

    series = Series.objects.filter(description__contains="MPRAGE").first()


Great! now all we need to do in order to get a NumPy_ :class:`~numpy.ndarray` of the underlying data would be::

    data = series.get_data()
    data.shape
    # Out: (224, 224, 208)

To inspect a particular slice, we could use matplotlib_::

    import matplotlib.pyplot as plt

    plt.imshow(data[:, :, 100])
    plt.show()

This should return a figure similar to this:

.. image:: images/image_plot.png
    :align: center
    :alt: Image could not be retrieved!


.. _DICOM: https://en.wikipedia.org/wiki/DICOM
.. _ZIP archives: https://en.wikipedia.org/wiki/Zip_(file_format)
.. _Series Description: https://dicom.innolitics.com/ciods/mr-image/general-series/0008103e
.. _NumPy: https://www.numpy.org/
.. _matplotlib: https://matplotlib.org/

.. rubric:: Footnotes

.. [#0] Brant-Zawadzki, M., Gillan, G. D., & Nitz, W. R. (1992). MP RAGE: a three-dimensional, T1-weighted, gradient-echo sequence--initial experience in the brain. Radiology, 182(3), 769-775.