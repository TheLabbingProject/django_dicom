Overview
========

`django_dicom` is a reusable `Django <https://www.djangoproject.com/>`_ application
built to maintain a database of `DICOM <https://en.wikipedia.org/wiki/DICOM>`_ data. It was
created to support the `pylabber <https://github.com/ZviBaratz/pylabber>`_ project, but
does not depend on it. `django_dicom` creates models that represent the various `DICOM <https://en.wikipedia.org/wiki/DICOM>`_
entities: :class:`~django_dicom.models.image.Image`, :class:`~django_dicom.models.series.Series`,
:class:`~django_dicom.models.study.Study`, and :class:`~django_dicom.models.patient.Patient`
(see `here <http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html>`_
and `here <http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html>`_ for more information). 

