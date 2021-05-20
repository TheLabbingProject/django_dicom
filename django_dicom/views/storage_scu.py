"""
Definition of the :class:`StorageScuViewSet` class.
"""

from django_dicom.filters import StorageScuFilter
from django_dicom.models.networking import StorageServiceClassUser
from django_dicom.serializers import StorageScuSerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from rest_framework import viewsets


class StorageScuViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows storage SCUs to be viewed or edited.

    """

    filter_class = StorageScuFilter
    pagination_class = StandardResultsSetPagination
    queryset = StorageServiceClassUser.objects.order_by("title")
    serializer_class = StorageScuSerializer
