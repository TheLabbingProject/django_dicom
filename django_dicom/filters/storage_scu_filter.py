"""
Definition of the :class:`StudyFilter` class.
"""
from django_dicom.models.networking import StorageServiceClassUser
from django_filters import rest_framework as filters


class StorageScuFilter(filters.FilterSet):
    """
    Provides filtering functionality for the
    :class:`~django_dicom.views.storage_scu.StorageScuViewSet`.

    Available filters are:

        * *id*: Primary key
        * *title*: Service Class User title
        * *ip*: Service Class User IP
    """

    class Meta:
        model = StorageServiceClassUser
        fields = (
            "id",
            "title",
            "ip",
        )
