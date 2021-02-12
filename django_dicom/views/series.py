import os

import pandas as pd
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django_dicom.filters import SeriesFilter
from django_dicom.models import Series
from django_dicom.serializers import SeriesSerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

CSV_COLUMNS = {
    "ID": "id",
    "EchoTime": "echo_time",
    "RepetitionTime": "repetition_time",
    "InversionTime": "inversion_time",
    "PixelSpacing": "pixel_spacing",
    "SliceThickness": "slice_thickness",
    "StudyDescription": "study__description",
    "SequenceName": "sequence_name",
    "PulseSequenceName": "pulse_sequence_name",
    "StudyTime": "study__time",
    "StudyDate": "study__date",
    "Manufacturer": "manufacturer",
    "ScanningSequence": "scanning_sequence",
    "SequenceVariant": "sequence_variant",
}


class SeriesViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows series to be viewed or edited.

    """

    filter_class = SeriesFilter
    ordering_fields = (
        "study",
        "patient",
        "number",
        "date",
        "time",
        "scanning_sequence",
        "sequence_variant",
        "pixel_spacing",
        "echo_time",
        "inversion_time",
        "repetition_time",
        "manufacturer",
        "manufacturer_model_name",
        "magnetic_field_strength",
        "device_serial_number",
        "institution_name",
    )
    pagination_class = StandardResultsSetPagination
    queryset = Series.objects.all().order_by("-date", "time")
    search_fields = (
        "study",
        "patient",
        "body_part_examined",
        "number",
        "description",
        "date",
        "time",
        "modality",
        "protocol_name",
        "scanning_sequence",
        "sequence_variant",
        "pixel_spacing",
        "echo_time",
        "inversion_time",
        "repetition_time",
        "flip_angle",
        "manufacturer",
        "manufacturer_model_name",
        "magnetic_field_strength",
        "device_serial_number",
        "institution_name",
        "uid",
    )
    serializer_class = SeriesSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(username=self.request.user)
        if user.is_staff:
            return Series.objects.all()
        return Series.objects.filter(
            scan__study_groups__study__collaborators=user
        )

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
