"""
Definition of the :class:`StudyViewSet` class.
"""
from django_dicom.filters import StudyFilter
from django_dicom.models import Study
from django_dicom.serializers import StudySerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from django_dicom.views.utils import STUDY_AGGREGATIONS
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class StudyViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows studies to be viewed or edited.
    """

    filter_class = StudyFilter
    pagination_class = StandardResultsSetPagination
    queryset = Study.objects.with_counts()
    serializer_class = StudySerializer

    @action(detail=False, methods=["get"])
    def aggregate(self, request) -> Response:
        result = self.queryset.aggregate(**STUDY_AGGREGATIONS)
        return Response(result)
