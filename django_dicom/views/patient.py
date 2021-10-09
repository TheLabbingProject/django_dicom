"""
Definition of the :class:`PatientViewSet` class.
"""
import os
from shutil import make_archive

from django.conf import settings
from django.http import FileResponse
from django_dicom.filters import PatientFilter
from django_dicom.models import Patient
from django_dicom.serializers import PatientSerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from django_dicom.views.utils import PATIENT_AGGREGATIONS
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PatientViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """

    filter_class = PatientFilter
    pagination_class = StandardResultsSetPagination
    queryset = Patient.objects.order_by(
        "family_name", "given_name"
    ).with_counts()
    serializer_class = PatientSerializer

    @action(detail=False, methods=["get"])
    def aggregate(self, request) -> Response:
        result = self.queryset.aggregate(**PATIENT_AGGREGATIONS)
        return Response(result)

    @action(detail=True, methods=["get"])
    def download_series_set(self, request, uid):
        scans_root = os.path.join(settings.MEDIA_ROOT, "MRI/DICOM")
        patient_path = os.path.join(scans_root, uid)
        patient_zip = patient_path + "_scans.zip"
        make_archive(patient_path + "_scans", "zip", patient_path)
        return FileResponse(open(patient_zip, "rb"), as_attachment=True)
