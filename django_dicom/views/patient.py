"""
Definition of the :class:`PatientViewSet` class.
"""
import os
from shutil import make_archive
from typing import Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.http import FileResponse
from django_dicom.filters import PatientFilter
from django_dicom.models import Patient
from django_dicom.serializers import PatientSerializer
from django_dicom.utils.configuration import ENABLE_COUNT_FILTERING
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.messages import COUNT_FILTERING_DISABLED
from django_dicom.views.pagination import StandardResultsSetPagination
from django_dicom.views.utils import PATIENT_AGGREGATIONS
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

DEFAULT_PATIENT_ORDERING: Tuple[str] = ("family_name", "given_name")
PATIENT_ORDERING_FIELDS: Tuple[str] = (
    "id",
    "uid",
    "family_name",
    "given_name",
    "sex",
    "date_of_birth",
    "latest_study_time",
)


class PatientViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """

    filter_class = PatientFilter
    pagination_class = StandardResultsSetPagination
    queryset = Patient.objects.order_by(
        *DEFAULT_PATIENT_ORDERING
    ).with_latest_study_time()
    serializer_class = PatientSerializer
    ordering_fields = PATIENT_ORDERING_FIELDS

    def get_queryset(self) -> QuerySet:
        """
        Overrides the parent :func:`get_queryset` method to apply aggregated
        annotation if count filtering is enabled.

        Returns
        -------
        QuerySet
            Patient queryset
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
            result = self.get_queryset().aggregate(**PATIENT_AGGREGATIONS)
        else:
            result = COUNT_FILTERING_DISABLED
        return Response(result)

    @action(detail=True, methods=["get"])
    def download_series_set(self, request, uid):
        scans_root = os.path.join(settings.MEDIA_ROOT, "MRI/DICOM")
        patient_path = os.path.join(scans_root, uid)
        patient_zip = patient_path + "_scans.zip"
        make_archive(patient_path + "_scans", "zip", patient_path)
        return FileResponse(open(patient_zip, "rb"), as_attachment=True)
