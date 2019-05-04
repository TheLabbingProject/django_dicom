"""
Provides `serializers <https://www.django-rest-framework.org/api-guide/serializers/>`_ for the
`REST API <https://www.django-rest-framework.org/topics/rest-hypermedia-hateoas/>`_.

"""

from django_dicom.serializers.image_serializer import ImageSerializer
from django_dicom.serializers.series_serializer import SeriesSerializer
from django_dicom.serializers.study_serializer import StudySerializer
from django_dicom.serializers.patient_serializer import PatientSerializer
