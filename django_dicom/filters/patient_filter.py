"""
Definition of the :class:`FilterSet` subclass that will be assigned to the
:class:`~django_dicom.views.patient.PatientViewSet`\'s
:attr:`~django_dicom.views.patient.PatientViewSet.filter_class` attribute value.
"""

from dicom_parser.utils.code_strings.sex import Sex
from django.db.models import QuerySet
from django_dicom.models.patient import Patient
from django_dicom.models.series import Series
from django_filters import rest_framework as filters


class PatientFilter(filters.FilterSet):
    """
    Provides filtering functionality for the
    :class:`~django_dicom.views.patient.PatientViewSet`.

    Available filters are:

        * *id*: Primary key
        * *uid*: Patient UID (contains, icontains, or exact)
        * *born_after_date*: Earliest date of birth
        * *born_before_date*: Latest date of birth
        * *name_prefix*: Any of the existing *name_prefix* values in the
          database
        * *given_name*: Given name value (contains, icontains, or exact)
        * *middle_name*: Middle name value (contains, icontains, or exact)
        * *family_name*: Family name value (contains, icontains, or exact)
        * *name_suffix*: Any of the existing *name_prefix* values in the
          database
        * *sex*: Any of the sex options defined in the
          :class:`~dicom_parser.utils.code_strings.sex.Sex`
          :class:`~enum.Enum`
        * *study__id*: Related :class:`~django_dicom.models.study.Study` ID
    """

    born_after_date = filters.DateFilter("date_of_birth", lookup_expr="gte")
    born_before_date = filters.DateFilter("date_of_birth", lookup_expr="lte")
    name_prefix = filters.AllValuesFilter("name_prefix")
    sex = filters.ChoiceFilter("sex", choices=Sex.choices())
    uid = filters.LookupChoiceFilter(
        lookup_choices=[
            ("contains", "Contains (case-sensitive)"),
            ("icontains", "Contains (case-insensitive)"),
            ("exact", "Exact"),
        ]
    )
    given_name = filters.LookupChoiceFilter(
        lookup_choices=[
            ("contains", "Contains (case-sensitive)"),
            ("icontains", "Contains (case-insensitive)"),
            ("exact", "Exact"),
        ]
    )
    middle_name = filters.LookupChoiceFilter(
        lookup_choices=[
            ("contains", "Contains (case-sensitive)"),
            ("icontains", "Contains (case-insensitive)"),
            ("exact", "Exact"),
        ]
    )
    family_name = filters.LookupChoiceFilter(
        lookup_choices=[
            ("contains", "Contains (case-sensitive)"),
            ("icontains", "Contains (case-insensitive)"),
            ("exact", "Exact"),
        ]
    )
    name_suffix = filters.AllValuesFilter("name_suffix")
    study__id = filters.NumberFilter(method="filter_by_study")

    class Meta:
        model = Patient
        fields = (
            "id",
            "uid",
            "born_after_date",
            "born_before_date",
            "name_prefix",
            "given_name",
            "middle_name",
            "family_name",
            "name_suffix",
        )

    def filter_by_study(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """
        Returns all :class:`~django_dicom.models.patient.Patient` instances
        that have :class:`~django_dicom.models.series.Series` instances
        belonging to the :class:`~django_dicom.models.study.Study` with the
        specified *value* as primary key.

        Used by
        :attr:`~django_dicom.filters.patient_filter.PatientFilter.study__id`.

        Parameters
        ----------
        queryset : :class:`~django.db.models.query.QuerySet`
            :class:`~django_dicom.models.patient.Patient` instances
        name : str
            Name of the queried filter field
        value : int
            :class:`~django_dicom.models.study.Study` primary key

        Returns
        -------
        :class:`~django.db.models.query.QuerySet`
            Filtered :class:`~django_dicom.models.patient.Patient` instances
        """

        if not value:
            return queryset
        series = Series.objects.filter(study__id=value)
        patient_ids = set(series.values_list("patient", flat=True))
        return queryset.filter(id__in=patient_ids)
