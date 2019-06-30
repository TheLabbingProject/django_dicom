from django_dicom.models.patient import Patient
from django_dicom.reader.code_strings.sex import Sex
from django_filters import rest_framework as filters


class PatientFilter(filters.FilterSet):
    """
    Provides useful filtering options for the :class:`~django_dicom.models.patient.Patient`
    class.
    
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
