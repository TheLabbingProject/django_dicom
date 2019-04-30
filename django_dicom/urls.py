from django.urls import path, include

from django_dicom import views
from rest_framework import routers

app_name = "django_dicom"


router = routers.DefaultRouter()
router.register(r"image", views.ImageViewSet)
router.register(r"series", views.SeriesViewSet)
router.register(r"study", views.StudyViewSet)
router.register(r"patient", views.PatientViewSet)

urlpatterns = [
    # path("new/", views.ImagesCreateView.as_view(), name="images_create"),
    # path("images/", views.ImageListView.as_view(), name="image_list"),
    # path("<int:pk>/", views.ImageDetailView.as_view(), name="image_detail"),
    # path("series/", views.SeriesListView.as_view(), name="series_list"),
    # path(
    #     "series/<int:pk>/", views.SeriesDetailView.as_view(), name="series_detail"
    # ),
    # path("studies/", views.StudyListView.as_view(), name="study_list"),
    # path("study/<int:pk>/", views.StudyDetailView.as_view(), name="study_detail"),
    # path("patients/", views.PatientListView.as_view(), name="patient_list"),
    # path(
    #     "patient/<int:pk>/",
    #     views.PatientDetailView.as_view(),
    #     name="patient_detail",
    # ),
    # path("new_patient/", views.NewPatientsListView.as_view(), name="new_patients"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
#     "dicom",
# )

# urlpatterns = [path("dicom/", include(dicom_patterns))]

