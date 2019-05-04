from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django_dicom.filters import ImageFilter, SeriesFilter, StudyFilter, PatientFilter
from django_dicom.models import Image, Series, Study, Patient
from django_dicom.serializers import (
    ImageSerializer,
    SeriesSerializer,
    StudySerializer,
    PatientSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, filters, permissions, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response


class DefaultsMixin:
    """
    Default settings for view authentication, permissions, filtering and pagination.
    
    """

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = 25
    paginate_by_param = "page_size"
    max_paginate_by = 100
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class ImageViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or edited.
    
    """

    queryset = Image.objects.all().order_by("-date", "time")
    serializer_class = ImageSerializer
    filter_class = ImageFilter
    search_fields = ("number", "date", "time", "uid")
    ordering_fields = ("series", "number", "date", "time")

    @detail_route(methods=["GET"])
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

    @detail_route(methods=["GET"])
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


class ImageListView(LoginRequiredMixin, ListView):
    model = Image
    template_name = "dicom/image/image_list.html"


class ImageDetailView(LoginRequiredMixin, DetailView):
    model = Image
    template_name = "dicom/image/image_detail.html"


class SeriesDetailView(LoginRequiredMixin, DetailView):
    model = Series
    template_name = "dicom/series/series_detail.html"


class SeriesListView(LoginRequiredMixin, ListView):
    model = Series
    template_name = "dicom/series/series_list.html"


class StudyDetailView(LoginRequiredMixin, DetailView):
    model = Study
    template_name = "dicom/study/study_detail.html"


class StudyListView(LoginRequiredMixin, ListView):
    model = Study
    template_name = "dicom/study/study_list.html"


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = "dicom/patient/patient_detail.html"


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = "dicom/patient/patient_list.html"


# class ImagesCreateView(LoginRequiredMixin, FormView):
#     form_class = CreateImagesForm
#     template_name = "dicom/image/image_create.html"
#     success_url = reverse_lazy("dicom:instance_list")
#     temp_file_name = "tmp.dcm"
#     temp_zip_name = "tmp.zip"

#     def post(self, request, *args, **kwargs):
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         if form.is_valid():
#             files = request.FILES.getlist("dcm_files")
#             for file in files:
#                 if file.name.endswith(".dcm"):
#                     Image.objects.from_dcm(file)
#                 elif file.name.endswith(".zip"):
#                     Image.objects.from_zip(file)
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)

# class NewPatientsListView(LoginRequiredMixin, ListView):
#     model = Patient
#     template_name = "dicom/patients/patient_list.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["patients"] = Patient.objects.filter(subject__isnull=True).all()
#         context["chosen"] = Patient.objects.filter(subject__isnull=True).first()
#         return context
