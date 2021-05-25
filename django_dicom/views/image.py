"""
Definition of the :class:`ImageViewSet` class.
"""
from django.contrib.auth import get_user_model
from django_dicom.filters import ImageFilter
from django_dicom.models import Image
from django_dicom.serializers import ImageSerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser


class ImageViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or edited.
    """

    filter_class = ImageFilter
    ordering_fields = ("series", "number", "date", "time")
    pagination_class = StandardResultsSetPagination
    parser_classes = (MultiPartParser,)
    queryset = Image.objects.all().order_by("-date", "time")
    search_fields = ("number", "date", "time", "uid")
    serializer_class = ImageSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(username=self.request.user)
        if user.is_staff:
            return Image.objects.all()
        return Image.objects.filter(
            series__scan__study_groups__study__collaborators=user
        )

    # def put(self, request, format=None):
    #     file_obj = request.data["file"]
    #     if file_obj.name.endswith(".dcm"):
    #         image, created = ImportImage(file_obj).run()
    #     elif file_obj.name.endswith(".zip"):
    #         content = ContentFile(file_obj.read())
    #         temp_file_name = default_storage.save("tmp.zip", content)
    #         temp_file_path = opj(settings.MEDIA_ROOT, temp_file_name)
    #         LocalImport.import_local_zip_archive(temp_file_path, verbose=False) # noqa: E501
    #         return Response(
    #             {"message": "Successfully imported ZIP archive!"},
    #             status=status.HTTP_201_CREATED,
    #         )
    #     if created:
    #         return Response(
    #             {"message": f"Success! [Image #{image.id}]"},
    #             status=status.HTTP_201_CREATED,
    #         )
    #     return Response(status=status.HTTP_204_NO_CONTENT)
