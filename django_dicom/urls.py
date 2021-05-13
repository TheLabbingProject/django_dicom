from django.urls import include, path
from rest_framework import routers

from django_dicom import views

app_name = "dicom"
router = routers.DefaultRouter()
router.register(r"image", views.ImageViewSet)
router.register(r"series", views.SeriesViewSet)
router.register(r"study", views.StudyViewSet)
router.register(r"patient", views.PatientViewSet)


urlpatterns = [
    path("dicom/", include(router.urls)),
    path(
        "dicom/patient/<str:uid>/download",
        views.PatientViewSet.as_view({"get": "download_series_set"}),
        name="download_series_set",
    ),
    path(
        "dicom/manufacturersList/",
        views.SeriesViewSet.as_view({"get": "get_manufacturers"}),
        name="get_manufacturers",
    ),
    path(
        "dicom/series/get_csv/",
        views.SeriesViewSet.as_view({"get": "get_csv"}),
        name="get_csv",
    ),
    path(
        "dicom/series/to_zip/<str:series_ids>/",
        views.SeriesViewSet.as_view({"get": "listed_zip"}),
        name="listed_zip",
    ),
    path(
        "dicom/series/<int:series_id>/to_zip/",
        views.SeriesViewSet.as_view({"get": "to_zip"}),
        name="to_zip",
    ),
]
