"""
Facilitates retrieval of `DICOM <https://en.wikipedia.org/wiki/DICOM>`__ `header information <https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction>`_
using the :class:`~django_dicom.reader.header_information.HeaderInformation` class. This functionality relies on a `DICOM <https://en.wikipedia.org/wiki/DICOM>`__
parser with a callable ``parser()`` method which accepts a :class:`~pydicom.dataelem.DataElement` instance and returns a parsed value. By default, the provided
:class:`~django_dicom.reader.parser.DicomParser` class will be used.

"""

from django_dicom.reader.parser import DicomParser
from django_dicom.reader.header_information import HeaderInformation
