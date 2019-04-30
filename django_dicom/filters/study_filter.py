from django_filters import rest_framework as filters
from django_dicom.models.study import Study


class StudyFilter(filters.FilterSet):
    """
    Provides useful filtering options for the :class:`~django_dicom.models.study.Study`
    class.
    
    """

    description = filters.LookupChoiceFilter(
        lookup_choices=[
            ("contains", "Contains (case-sensitive)"),
            ("icontains", "Contains (case-insensitive)"),
            ("exact", "Exact"),
        ]
    )
    created_after_date = filters.DateFilter("date", lookup_expr="gte")
    created_before_date = filters.DateFilter("date", lookup_expr="lte")
    created_after_time = filters.DateFilter("time", lookup_expr="gte")
    created_before_time = filters.DateFilter("time", lookup_expr="lte")

    class Meta:
        model = Study
        fields = (
            "id",
            "uid",
            "description",
            "created_after_date",
            "created_before_date",
            "created_after_time",
            "created_before_time",
        )
