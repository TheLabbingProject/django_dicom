from django_dicom.filters import StudyFilter
from django_dicom.models import Study
from django_dicom.serializers import StudySerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from rest_framework import viewsets


class StudyViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows studies to be viewed or edited.
    
    """

    filter_class = StudyFilter
    pagination_class = StandardResultsSetPagination
    queryset = Study.objects.all().order_by("date", "time")
    serializer_class = StudySerializer
