"""
Creates `models <https://docs.djangoproject.com/en/2.2/topics/db/models/>`__ to represent the various 
`DICOM <https://en.wikipedia.org/wiki/DICOM>`__ entities: :class:`~django_dicom.models.image.Image`, :class:`~django_dicom.models.series.Series`,
:class:`~django_dicom.models.study.Study`, and :class:`~django_dicom.models.patient.Patient` 
(see `here <http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html>`__
and `here <http://dicomiseasy.blogspot.com/2011/12/chapter-4-dicom-objects-in-chapter-3.html>`__ for more information).

The relationship between entities in `django_dicom`:

.. image:: images/models.png
    :align: center
    :alt: Image could not be retrieved!

"""

from django_dicom.models.image import Image
from django_dicom.models.series import Series
from django_dicom.models.patient import Patient
from django_dicom.models.study import Study
