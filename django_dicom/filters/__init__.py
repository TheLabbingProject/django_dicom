"""
Provides filter classes for the REST API endpoints (`more information <https://www.django-rest-framework.org/api-guide/filtering/#generic-filtering>`_).


"""


from django_dicom.filters.image_filter import ImageFilter
from django_dicom.filters.series_filter import SeriesFilter
from django_dicom.filters.study_filter import StudyFilter
from django_dicom.filters.patient_filter import PatientFilter
