"""
Definition of the :class:`StudyViewSet` class.
"""
from typing import Tuple

from django.db.models import QuerySet
from django_dicom.filters import StudyFilter
from django_dicom.models import Study
from django_dicom.serializers import StudySerializer
from django_dicom.utils.configuration import ENABLE_COUNT_FILTERING
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.messages import COUNT_FILTERING_DISABLED
from django_dicom.views.pagination import StandardResultsSetPagination
from django_dicom.views.utils import STUDY_AGGREGATIONS
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

DEFAULT_STUDY_ORDERING: Tuple[str] = ("-date", "-time")


class StudyViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows studies to be viewed or edited.
    """

    filter_class = StudyFilter
    pagination_class = StandardResultsSetPagination
    queryset = Study.objects.order_by(*DEFAULT_STUDY_ORDERING)
    serializer_class = StudySerializer

    def get_queryset(self) -> QuerySet:
        """
        Overrides the parent :func:`get_queryset` method to apply aggregated
        annotation if count filtering is enabled.

        Returns
        -------
        QuerySet
            Study queryset
        """
        queryset = super().get_queryset()
        return queryset.with_counts() if ENABLE_COUNT_FILTERING else queryset

    @action(detail=False, methods=["get"])
    def aggregate(self, request) -> Response:
        """
        Returns related model counts if count filtering is enabled.

        Parameters
        ----------
        request : Request
            API request

        Returns
        -------
        Response
            Aggregated queryset or informational message
        """
        if ENABLE_COUNT_FILTERING:
            result = self.get_queryset().aggregate(**STUDY_AGGREGATIONS)
        else:
            result = COUNT_FILTERING_DISABLED
        return Response(result)
