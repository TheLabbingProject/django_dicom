"""
Definition of the :class:`SeriesViewSet` class.
"""
import io
import os
import zipfile
from pathlib import Path

import pandas as pd
from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponse
from django_dicom.filters import SeriesFilter
from django_dicom.models import Series
from django_dicom.serializers import SeriesSerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from django_dicom.views.utils import (
    CONTENT_DISPOSITION,
    CSV_COLUMNS,
    SERIES_OREDRING_FIELDS,
    SERIES_SEARCH_FIELDS,
    ZIP_CONTENT_TYPE,
)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class SeriesViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows series to be viewed or edited.
    """

    filter_class = SeriesFilter
    ordering_fields = SERIES_OREDRING_FIELDS
    pagination_class = StandardResultsSetPagination
    queryset = Series.objects.all().order_by("-date", "-time")
    search_fields = SERIES_SEARCH_FIELDS
    serializer_class = SeriesSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(username=self.request.user)
        if user.is_staff:
            return Series.objects.all()
        return Series.objects.filter(scan__study_groups__study__collaborators=user)

    @action(detail=False, methods=["get"])
    def get_manufacturers(self, request):
        queryset = self.get_queryset()
        manufacturers = set(
            value
            for value in queryset.values_list("manufacturer", flat=True)
            if value is not None
        )
        data = {"results": manufacturers}
        return Response(data)

    @action(detail=False, methods=["GET"])
    def get_csv(self, request: Request) -> Response:
        filename = "filtered_series.csv"
        series = self.filter_queryset(self.get_queryset())
        columns = dict(enumerate(CSV_COLUMNS.keys()))
        series = series.values_list(*list(CSV_COLUMNS.values()))
        output = pd.DataFrame.from_records(series).rename(columns=columns)
        output.to_csv(filename, encoding="utf-8-sig", index=False)
        response = FileResponse(open(filename, "rb"), as_attachment=True)
        os.unlink(filename)
        return response

    @action(detail=True, methods=["get"])
    def to_zip(self, request: Request, pk: int) -> FileResponse:
        instance = Series.objects.get(id=pk)
        patient_uid = instance.patient.uid
        date = instance.date.strftime("%Y%m%d")
        name = f"{patient_uid}_{date}_{instance.description}"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for dcm in Path(instance.path).iterdir():
                zip_file.write(dcm, dcm.name)
        response = HttpResponse(buffer.getvalue(), content_type=ZIP_CONTENT_TYPE)
        content_disposition = CONTENT_DISPOSITION.format(name=name)
        response["Content-Disposition"] = content_disposition
        return response

    @action(detail=False, methods=["get"])
    def listed_zip(self, request: Request, series_ids: str) -> FileResponse:
        series_ids = [int(pk) for pk in series_ids.split(",")]
        queryset = Series.objects.filter(id__in=series_ids)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for instance in queryset:
                p = Path(instance.path)
                for dcm in p.iterdir():
                    name = dcm.relative_to(p.parent.parent)
                    zip_file.write(dcm, name)
        response = HttpResponse(buffer.getvalue(), content_type=ZIP_CONTENT_TYPE)
        content_disposition = CONTENT_DISPOSITION.format(name="scans")
        response["Content-Disposition"] = content_disposition
        return response
