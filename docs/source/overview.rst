Overview
========

`django_dicom` is a reusable `Django <https://www.djangoproject.com/>`_ application
built to maintain a database of `DICOM <https://en.wikipedia.org/wiki/DICOM>`_ data. It was
created to support the `pylabber <https://github.com/ZviBaratz/pylabber>`_ project, but
does not depend on it. `django_dicom` creates `models <https://docs.djangoproject.com/en/2.2/topics/db/models/>`_
that represent the various `DICOM <https://en.wikipedia.org/wiki/DICOM>`_
entities: :class:`~django_dicom.models.image.Image`, :class:`~django_dicom.models.series.Series`,
:class:`~django_dicom.models.study.Study`, and :class:`~django_dicom.models.patient.Patient`
(see `here <http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html>`__
and `here <http://dicomiseasy.blogspot.com/2011/12/chapter-4-dicom-objects-in-chapter-3.html>`__ for more information)
and provides utility methods to import data and easily maintain the DICOM entities and their relationship.
Once data is imported, `Django's <https://www.fullstackpython.com/django-orm.html>`_
`ORM <https://www.fullstackpython.com/object-relational-mappers-orms.html>`_ 
provides us with powerful `querying <https://docs.djangoproject.com/en/2.1/topics/db/queries/>`_
abilities.

The purposed of this `reusable Django application <https://docs.djangoproject.com/en/2.2/intro/reusable-apps/>`_
is to create a centralized solution for DICOM data management in the context of of academic
research. It is being written as a local solution for `Tel Aviv University <https://english.tau.ac.il/>`_'s
`neuroimaging lab <http://neuroimaging.tau.ac.il/>`_.


