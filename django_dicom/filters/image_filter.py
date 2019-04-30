from django_filters import rest_framework as filters
from django_dicom.models.image import Image


class ImageFilter(filters.FilterSet):
    """
    Provides useful filtering options for the :class:`~django_dicom.models.image.Image`
    class.
    
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

    class Meta:
        model = Image
        fields = (
            "id",
            "uid",
            "series_uid",
            "series_description",
            "created_after_date",
            "created_before_date",
            "created_after_time",
            "created_before_time",
            "number",
        )
