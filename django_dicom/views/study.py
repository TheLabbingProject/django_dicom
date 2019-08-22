from django_dicom.filters import StudyFilter
from django_dicom.models import Study
from django_dicom.serializers import StudySerializer
from django_dicom.views.defaults import DefaultsMixin
from rest_framework import viewsets


class StudyViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows studies to be viewed or edited.
    
    """

    queryset = Study.objects.all().order_by("date", "time")
    serializer_class = StudySerializer
    filter_class = StudyFilter
