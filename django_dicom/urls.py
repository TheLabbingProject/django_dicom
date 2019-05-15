from django.urls import path, include

from django_dicom import views
from rest_framework import routers

app_name = "dicom"
router = routers.DefaultRouter()
router.register(r"image", views.ImageViewSet)
router.register(r"series", views.SeriesViewSet)
router.register(r"study", views.StudyViewSet)
router.register(r"patient", views.PatientViewSet)

dicom_patterns = (
    [
        # path("new/", views.ImagesCreateView.as_view(), name="images_create"),
        path("image/", views.ImageListView.as_view(), name="image_list"),
        path("image/<int:pk>/", views.ImageDetailView.as_view(), name="image_detail"),
        path("series/", views.SeriesListView.as_view(), name="series_list"),
        path(
            "series/<int:pk>/", views.SeriesDetailView.as_view(), name="series_detail"
        ),
        path("study/", views.StudyListView.as_view(), name="study_list"),
        path("study/<int:pk>/", views.StudyDetailView.as_view(), name="study_detail"),
        path("patient/", views.PatientListView.as_view(), name="patient_list"),
        path(
            "patient/<int:pk>/",
            views.PatientDetailView.as_view(),
            name="patient_detail",
        ),
        # path("new_patient/", views.NewPatientsListView.as_view(), name="new_patients"),
    ],
    app_name,
)

urlpatterns = [
    path("", include(dicom_patterns)),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

