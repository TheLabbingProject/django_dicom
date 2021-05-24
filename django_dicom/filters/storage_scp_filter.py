"""
Definition of the :class:`StudyFilter` class.
"""
from django_dicom.models.networking import StorageServiceClassProvider
from django_filters import rest_framework as filters


class StorageScpFilter(filters.FilterSet):
    """
    Provides filtering functionality for the
    :class:`~django_dicom.views.storage_scp.StorageScpViewSet`.

    Available filters are:

        * *id*: Primary key
        * *title*: Service Class User title
        * *ip*: Service Class User IP
    """

    class Meta:
        model = StorageServiceClassProvider
        fields = (
            "id",
            "title",
            "ip",
        )
