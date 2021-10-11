"""
Definition of the :class:`StudyFilter` class.
"""
from django_dicom.filters.utils import DEFAULT_LOOKUP_CHOICES
from django_dicom.models.study import Study
from django_dicom.utils.configuration import ENABLE_COUNT_FILTERING
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

    uid = filters.LookupChoiceFilter(lookup_choices=DEFAULT_LOOKUP_CHOICES)
    description = filters.LookupChoiceFilter(
        lookup_choices=DEFAULT_LOOKUP_CHOICES
    )
    date = filters.DateFromToRangeFilter()
    time_after = filters.TimeFilter("time", lookup_expr="gte")
    time_before = filters.TimeFilter("time", lookup_expr="lte")
    if ENABLE_COUNT_FILTERING:
        n_patients = filters.RangeFilter(
            label="Number of associated patients between:"
        )
        n_series = filters.RangeFilter(
            label="Number of associated series between:"
        )
        n_images = filters.RangeFilter(
            label="Number of associated images between:"
        )

    class Meta:
        model = Study
        fields = ("id",)
