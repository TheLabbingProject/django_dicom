Reading Header Information
--------------------------

DICOM_ images have a lot of infomation stored in `header tags <https://www.dicomlibrary.com/dicom/dicom-tags/>`_.
`django_dicom` includes a :mod:`~django_dicom.reader` package that includes both a :class:`~django_dicom.reader.header_information.HeaderInformation` class
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



.. _DICOM: https://en.wikipedia.org/wiki/DICOM