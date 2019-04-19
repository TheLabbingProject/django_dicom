from django.urls import path

from django_dicom import views

app_name = "django_dicom"

urlpatterns = [
    path("new/", views.ImagesCreateView.as_view(), name="images_create"),
    path("images/", views.ImageListView.as_view(), name="instance_list"),
    path("<int:pk>/", views.ImageDetailView.as_view(), name="instance_detail"),
    path("series/", views.SeriesListView.as_view(), name="series_list"),
    path("series/<int:pk>/", views.SeriesDetailView.as_view(), name="series_detail"),
    path("studies/", views.StudyListView.as_view(), name="study_list"),
    path("study/<int:pk>/", views.StudyDetailView.as_view(), name="study_detail"),
    path("patients/", views.PatientListView.as_view(), name="patient_list"),
    path(
        "patients/<int:pk>/", views.PatientDetailView.as_view(), name="patient_detail"
    ),
    path("new_patients/", views.NewPatientsListView.as_view(), name="new_patients"),
]
