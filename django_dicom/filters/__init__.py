"""
Provides filter classes for the `REST API`_ endpoints (for more information see
the `DRF docs`__ and `django-filter`_\'s `integration with DRF`_ docs).

__ https://www.django-rest-framework.org/api-guide/filtering/#generic-filtering
.. _django-filter: https://github.com/carltongibson/django-filter
.. _integration with DRF:
   https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html
.. _REST API: https://en.wikipedia.org/wiki/Representational_state_transfer
"""


from django_dicom.filters.image_filter import ImageFilter
from django_dicom.filters.patient_filter import PatientFilter
from django_dicom.filters.series_filter import SeriesFilter
from django_dicom.filters.study_filter import StudyFilter
