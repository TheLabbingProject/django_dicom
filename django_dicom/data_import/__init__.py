"""
Provides classes that supervise data import. These classes manage the creation and association
of `DICOM <https://en.wikipedia.org/wiki/DICOM>`__ entities (see `here <http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html>`__
and `here <http://dicomiseasy.blogspot.com/2011/12/chapter-4-dicom-objects-in-chapter-3.html>`__ for more information).

"""

from django_dicom.data_import.import_image import ImportImage
from django_dicom.data_import.local_import import LocalImport
