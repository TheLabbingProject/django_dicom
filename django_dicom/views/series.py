from django.contrib.auth import get_user_model
from django_dicom.filters import SeriesFilter
from django_dicom.models import Series
from django_dicom.serializers import SeriesSerializer
from django_dicom.views.defaults import DefaultsMixin
from rest_framework import viewsets


class SeriesViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows series to be viewed or edited.
    
    """

    queryset = Series.objects.all().order_by("-date", "time")
    serializer_class = SeriesSerializer
    filter_class = SeriesFilter
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

    def get_queryset(self):
        user = get_user_model().objects.get(username=self.request.user)
        if user.is_staff:
            return Series.objects.all()
        return Series.objects.filter(scan__study_groups__study__collaborators=user)
