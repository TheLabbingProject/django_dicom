from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django_dicom.forms import CreateImagesForm
from django_dicom.models import Image, Series, Study, Patient


class ImageListView(LoginRequiredMixin, ListView):
    model = Image
    template_name = "dicom/instances/instance_list.html"


class ImageDetailView(LoginRequiredMixin, DetailView):
    model = Image
    template_name = "dicom/instances/instance_detail.html"


class ImagesCreateView(LoginRequiredMixin, FormView):
    form_class = CreateImagesForm
    template_name = "dicom/instances/instances_create.html"
    success_url = reverse_lazy("dicom:instance_list")
    temp_file_name = "tmp.dcm"
    temp_zip_name = "tmp.zip"

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            files = request.FILES.getlist("dcm_files")
            for file in files:
                if file.name.endswith(".dcm"):
                    Image.objects.from_dcm(file)
                elif file.name.endswith(".zip"):
                    Image.objects.from_zip(file)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class SeriesDetailView(LoginRequiredMixin, DetailView):
    model = Series
    template_name = "dicom/series/series_detail.html"


class SeriesListView(LoginRequiredMixin, ListView):
    model = Series
    template_name = "dicom/series/series_list.html"


class StudyDetailView(LoginRequiredMixin, DetailView):
    model = Study
    template_name = "dicom/studies/study_detail.html"


class StudyListView(LoginRequiredMixin, ListView):
    model = Study
    template_name = "dicom/studies/study_list.html"


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = "dicom/patients/patient_detail.html"


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = "dicom/patients/patient_list.html"


class NewPatientsListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = "dicom/patients/patient_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patients"] = Patient.objects.filter(subject__isnull=True).all()
        context["chosen"] = Patient.objects.filter(subject__isnull=True).first()
        return context
