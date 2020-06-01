Reading Series Data
-------------------

`django_dicom` relies on dicom_parser_ and pydicom_'s to convert an
:class:`~django_dicom.models.image.Image`\'s pixel data from bytes to a
NumPy_ :class:`~numpy.ndarray`.

Let's query an anatomical ("MPRAGE"[#0]_) :class:`~django_dicom.models.series.Series` instance we've added based on its `Series Description`_::

    >>> from django_dicom.models import Series
    >>> series = Series.objects.filter(description__contains="MPRAGE").first()


Great! now all we need to do in order to get a NumPy_
:class:`~numpy.ndarray` of the underlying data would be to use the
:attr:`~django_dicom.models.series.Series.data` property::

    >>> data = series.get_data()
    >>> series.data.shape
    (224, 224, 208)

To inspect a particular slice, we could use matplotlib_::

    >>> import matplotlib.pyplot as plt
    >>> plt.imshow(series.data[:, :, 100])
    >>> plt.show()

This should return a figure similar to this:

.. image:: images/image_plot.png
    :align: center
    :alt: Image could not be retrieved!

.. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/
.. _matplotlib: https://matplotlib.org/
.. _NumPy: https://www.numpy.org/
.. _pydicom: https://github.com/pydicom/pydicom
.. _Series Description: https://dicom.innolitics.com/ciods/mr-image/general-series/0008103e


.. rubric:: Footnotes

.. [#0] Brant-Zawadzki, M., Gillan, G. D., & Nitz, W. R. (1992). MP RAGE: a three-dimensional, T1-weighted, gradient-echo sequence--initial experience in the brain. Radiology, 182(3), 769-775.