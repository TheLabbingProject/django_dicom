from os.path import join as opj

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_dicom.data_import import ImportImage, LocalImport
from django_dicom.filters import ImageFilter, SeriesFilter, StudyFilter, PatientFilter
from django_dicom.models import Image, Series, Study, Patient
from django_dicom.serializers import (
    ImageSerializer,
    SeriesSerializer,
    StudySerializer,
    PatientSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class DefaultsMixin:
    """
    Default settings for view authentication, permissions, filtering and pagination.
    
    """

    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)


class ImageViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or edited.
    
    """

    filter_class = ImageFilter
    ordering_fields = ("series", "number", "date", "time")
    parser_classes = (MultiPartParser,)
    queryset = Image.objects.all().order_by("-date", "time")
    search_fields = ("number", "date", "time", "uid")
    serializer_class = ImageSerializer

    def put(self, request, format=None):
        file_obj = request.data["file"]
        if file_obj.name.endswith(".dcm"):
            image, created = ImportImage(file_obj).run()
        elif file_obj.name.endswith(".zip"):
            content = ContentFile(file_obj.read())
            temp_file_name = default_storage.save("tmp.zip", content)
            temp_file_path = opj(settings.MEDIA_ROOT, temp_file_name)
            LocalImport.import_local_zip_archive(temp_file_path, verbose=False)
            return Response(
                {"message": "Successfully imported ZIP archive!"},
                status=status.HTTP_201_CREATED,
            )
        if created:
            return Response(
                {"message": f"Success! [Image #{image.id}]"},
                status=status.HTTP_201_CREATED,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def pixel_data(self, request, pk: int = None):
        """
        Returns the instance's pixel array as a :class:`~rest_framework.response.Response`.
        
        Parameters
        ----------
        request : :class:`~rest_framework.request.Request`
            The request object.
        pk : int, optional
            The requested object's primary key, by default None
        
        Returns
        -------
        :class:`~rest_framework.response.Response`
            Image pixel data as a response.
        """
        image = self.get_object()
        if image:
            return Response(image.get_data(as_json=True))
        return Response("Invalid image ID!", status=status.HTTP_404_NOT_FOUND)


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

    @action(detail=True)
    def pixel_data(self, request, pk: int = None):
        """
        Returns the instance's pixel array as a :class:`~rest_framework.response.Response`.
        
        Parameters
        ----------
        request : :class:`~rest_framework.request.Request`
            The request object.
        pk : int, optional
            The requested object's primary key, by default None
        
        Returns
        -------
        :class:`~rest_framework.response.Response`
            Series pixel data as a response.
        """

        series = self.get_object()
        if series:
            return Response(series.get_data(as_json=True))
        return Response("Invalid series ID!", status=status.HTTP_404_NOT_FOUND)


class PatientViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    
    """

    queryset = Patient.objects.all().order_by("family_name", "given_name")
    serializer_class = PatientSerializer
    filter_class = PatientFilter


class StudyViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows studies to be viewed or edited.
    
    """

    queryset = Study.objects.all().order_by("date", "time")
    serializer_class = StudySerializer
    filter_class = StudyFilter
