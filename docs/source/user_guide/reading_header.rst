Reading Header Information
==========================

*django_dicom* uses the dicom_parser_ package to read header information and
store it as an :class:`~django_dicom.models.header.Header` instance. Some
information is already available to us directly through the values stored in
the associated
:class:`~django_dicom.models.image.Image`,
:class:`~django_dicom.models.series.Series`,
:class:`~django_dicom.models.patient.Patient`, and
:class:`~django_dicom.models.study.Study` instances. However,
:class:`~django_dicom.models.header.Header` instances are collections of
:class:`~django_dicom.models.data_element.DataElement` instances, each
storing a queryable reference to both the raw and parsed values of a given
data element.

By defualt, *django_dicom* will store all official DICOM tags,
skipping any private data elements. These will still be easily readable,
however, we will not be able to query them from the database. For more
information about import modes, see :ref:`user_guide/import_modes:Import Modes`.

Reading a Single Image's Header
-------------------------------

To read a single :class:`~django_dicom.models.image.Image` instance's header,
we can simply use the :attr:`~django_dicom.models.image.Image.instance` property
to retrieve dicom_parser_\'s representation of a DICOM image (
:class:`~dicom_parser.image.Image`):

.. code-block:: python

    >>> from django_dicom.models import Image

    >>> image = Image.objects.first()
    >>> image.instance.header
                Keyword                      VR                VM  Value
    Tag
    (0008, 0005)  SpecificCharacterSet         Code String       1   ISO_IR 100
    (0008, 0008)  ImageType                    Code String       5   ['ORIGINAL', 'PRIMARY', ...
    (0008, 0012)  InstanceCreationDate         Date              1   2019-12-18
    (0008, 0013)  InstanceCreationTime         Time              1   08:54:41.479000
    (0008, 0016)  SOPClassUID                  Unique Identifer  1   1.2.840.10008.5.1.4.1.1.4
    (0008, 0018)  SOPInstanceUID               Unique Identifer  1   1.3.12.2.1107.5.2.43.660...
    (0008, 0020)  StudyDate                    Date              1   2019-12-18
    ...
    Private Data Elements
    =====================
                Keyword                      VR           VM  Value
    Tag
    (0019, 0010)                               Long String  1   SIEMENS MR HEADER
    (0019, 1008)  CsaImageHeaderType           Unknown      1   b'IMAGE NUM 4 '
    (0019, 1009)  CsaImageHeaderVersion??      Unknown      1   b'1.0 '
    (0019, 100b)  SliceMeasurementDuration     Unknown      1                          3535
    ...

    >>> image.instance.header.get('PixelSpacing')
    [0.48828125, 0.48828125]

For more information on dicom_parser_\'s classes and functionality, see `the
documentation`_.

Querying the Database
---------------------

According to the chosen :ref:`import mode <user_guide/import_modes:Import Modes>`,
no, some, or all of the saved images' data elements will be serialized to the
database as :class:`~django_dicom.models.data_element.DataElement` instances.
Each :class:`~django_dicom.models.data_element.DataElement` represents a single
tag within a single header, however, the actual information is available its
:attr:`~django_dicom.models.data_element.DataElement.definition` and
:attr:`~django_dicom.models.data_element.DataElement.value` attributes.
These attributes associate the
:class:`~django_dicom.models.data_element.DataElement` instance with reusable
:class:`~django_dicom.models.data_element_definition.DataElementDefinition`
and :class:`~django_dicom.models.values.data_element_value.DataElementValue` instances,
thereby preventing data duplication simplifying queries.

To better understand the way header information is serialized in the database,
let's query all the :class:`~django_dicom.models.series.Series` instances in
which the underlying image headers contain a data element named *ImageType*
which contains a value of *MOSAIC*.

First, we'll have a look at the relevant
:class:`~django_dicom.models.data_element_definition.DataElementDefinition`
instance:

.. code:: python

    >>> from django_dicom.models import DataElementDefinition
    >>> definition = DataElementDefinition.objects.get(keyword="ImageType")
    >>> definition
    <DataElementDefinition:
    Tag                     (0008, 0008)
    Keyword                    ImageType
    Value Representation              CS
    Description               Image Type>

Now, let's select any
:class:`~django_dicom.models.values.data_element_value.DataElementValue` instances
satisfying our condition:

.. code:: python

    >>> from django_dicom.models import CodeString
    >>> values = CodeString.objects.filter(value="MOSAIC")
    >>> values.count()
    9

This means there are 9 different distinct *ImageType* values that contain the
string *MOSAIC*. If we want all the related
:class:`~django_dicom.models.data_element.DataElement` instances, we could:

.. code:: python

    >>> from django_dicom.models import DataElement
    >>> data_elements = DataElement.objects.filter(definition=definition, _values__in=values)
    >>> data_elements.count()
    42236

Two important things to note here:

    * We used the :attr:`~django_dicom.models.data_element.DataElement._values`
      attribute to access the raw relationship between the
      :class:`~django_dicom.models.data_element.DataElement` and its associated
      :class:`~django_dicom.models.values.data_element_value.DataElementValue`\s.
    * We used *__in* to query this `ManyToMany relationship`_ and retrieve data
      elements containing any of the desired values. This is necessary because
      DICOM elements may have multiple values (for more information see
      `value multiplicity`_).

Now, if we would like to query all the images to which these data elements belong:

.. code:: python

    >>> image_ids = data_elements.values_list('header__image', flat=True)
    >>> images = Image.objects.filter(id__in=image_ids)

or the series:

.. code:: python

    >>> from django_dicom.models import Series
    >>> series_ids = images.values_list('series', flat=True)
    >>> series = Series.objects.filter(id__in=series_ids)
    >>> series.count()
    409
    >>> series.first().description
    'IR-DTI_30dir_3iso'

.. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/
.. _ManyToMany relationship: https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_many/
.. _the documentation: https://dicom-parser.readthedocs.io/en/latest/
.. _value multiplicity: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_6.4.html