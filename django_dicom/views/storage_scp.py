"""
Definition of the :class:`StorageScpViewSet` class.
"""

from django_dicom.filters import StorageScpFilter
from django_dicom.models.networking import StorageServiceClassProvider
from django_dicom.serializers import StorageScpSerializer
from django_dicom.views.defaults import DefaultsMixin
from django_dicom.views.pagination import StandardResultsSetPagination
from rest_framework import viewsets


class StorageScpViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows storage SCUs to be viewed or edited.
    """

    filter_class = StorageScpFilter
    pagination_class = StandardResultsSetPagination
    queryset = StorageServiceClassProvider.objects.order_by("title")
    serializer_class = StorageScpSerializer
