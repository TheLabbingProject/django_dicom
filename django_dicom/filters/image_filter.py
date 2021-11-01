"""
Definition of the :class:`ImageFilter` class.
"""
from django_dicom.models.image import Image
from django_dicom.models.utils.sequence_type import SEQUENCE_TYPE_CHOICES
from django_filters import rest_framework as filters


class ImageFilter(filters.FilterSet):
    """
    Provides filtering functionality for the
    :class:`~django_dicom.views.image.ImageViewSet`.

    Available filters are:

        * *id*: Primary key
        * *series_uid*: Series instance UID (contains)
        * *series_description*: Series description (contains)
        * *number*: Series number (exact)
        * *created_after_date*: Create after date
        * *created_before_date*: Create before date
        * *created_after_time*: Create after time
        * *created_before_time*: Create before time
    """

    series_uid = filters.CharFilter(
        "series__uid", lookup_expr="contains", label="Series UID"
    )
    series_description = filters.CharFilter(
        "series__description",
        lookup_expr="contains",
        label="Series description contains",
    )
    created_after_date = filters.DateFilter("date", lookup_expr="gte")
    created_before_date = filters.DateFilter("date", lookup_expr="lte")
    created_after_time = filters.DateFilter("time", lookup_expr="gte")
    created_before_time = filters.DateFilter("time", lookup_expr="lte")
    sequence_type = filters.MultipleChoiceFilter(
        "series__sequence_type", choices=SEQUENCE_TYPE_CHOICES
    )

    class Meta:
        model = Image
        fields = (
            "id",
            "uid",
            "number",
        )
