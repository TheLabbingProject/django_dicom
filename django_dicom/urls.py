from django.urls import path, include
from django_dicom import views
from rest_framework import routers

app_name = "dicom"
router = routers.DefaultRouter()
router.register(r"images", views.ImageViewSet)
router.register(r"series", views.SeriesViewSet)
router.register(r"studies", views.StudyViewSet)
router.register(r"patients", views.PatientViewSet)


urlpatterns = [path("dicom/", include(router.urls))]

