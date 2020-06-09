Overview
========

`django_dicom` is a reusable Django_ application built to maintain a database
of DICOM_ data. It was created to support the pylabber_ project, but does not
depend on it. *django_dicom* creates :class:`~django.db.models.Model`
sub-classes that represent the various DICOM entities (see `the DICOM standard
specification`_ and `this blog post`_ for more information) and provides
utility methods to import data and easily maintain the DICOM entities and their
relationship. Once data is imported, `Django's
<https://www.fullstackpython.com/django-orm.html>`_ ORM_ provides us with
powerful querying abilities.

.. image:: images/models.png
    :align: center
    :alt: Image could not be retrieved!

The purposed of this `reusable Django application
<https://docs.djangoproject.com/en/2.2/intro/reusable-apps/>`_ is to create a
centralized solution for DICOM data management in the context of of academic
research. It is being built as a databasing solution for `Tel Aviv University`_
\'s `neuroimaging lab`_.

.. _DICOM: https://en.wikipedia.org/wiki/DICOM
.. _Django: https://www.djangoproject.com
.. _neuroimaging lab: http://neuroimaging.tau.ac.il
.. _ORM: https://www.fullstackpython.com/object-relational-mappers-orms.html
.. _pylabber: https://github.com/TheLabbingProject/pylabber
.. _Tel Aviv University: https://english.tau.ac.il/
.. _the DICOM standard specification:
   http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html
.. _this blog post:
   http://dicomiseasy.blogspot.com/2011/12/chapter-4-dicom-objects-in-chapter-3.html