"""
Definition of the :class:`FilterSet` subclass that will be assigned to the
:class:`~django_dicom.views.study.StudyViewSet`\'s
:attr:`~django_dicom.views.study.StudyViewSet.filter_class` attribute value.
"""


from django_dicom.models.study import Study
from django_filters import rest_framework as filters


class StudyFilter(filters.FilterSet):
    """
    Provides filtering functionality for the
    :class:`~django_dicom.views.study.StudyViewSet`.

    Available filters are:

        * *id*: Primary key
        * *uid*: Study instance UID
        * *description*: Study description (contains, icontains, or exact)
        * *created_after_date*: Create after date
        * *created_before_date*: Create before date
        * *created_after_time*: Create after time
        * *created_before_time*: Create before time
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
