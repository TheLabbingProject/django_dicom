from django.db.models import QuerySet
from django_filters import rest_framework as filters
from django_dicom.models.series import Series
from django_dicom.reader.code_strings import Modality, ScanningSequence, SequenceVariant


def filter_array(queryset: QuerySet, field_name: str, value: list):
    """
    Returns an exact lookup for a PostgreSQL ArrayField_.

    .. _ArrayField: https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/#arrayfield
    
    Parameters
    ----------
    queryset : :class:`~django.db.models.QuerySet`
        The filtered queryset.
    field_name : str
        The name of the field the queryset is being filtered by.
    value : list
        The values to filter by.
    """

    if not value:
        return queryset
    # We check both content and length in order to return only exact matches
    contains = f"{field_name}__contains"
    length = f"{field_name}__len"
    return queryset.filter(**{contains: value, length: len(value)}).all()


class SeriesFilter(filters.FilterSet):
    """
    Provides useful filtering options for the :class:`~django_dicom.models.series.Series`
    class.
    
    """

    study_uid = filters.CharFilter("study__uid", lookup_expr="exact", label="Study UID")
    study_description = filters.CharFilter(
        "study__description", lookup_expr="contains", label="Study description contains"
    )
    modality = filters.ChoiceFilter("modality", choices=Modality.choices())
    description = filters.LookupChoiceFilter(
        lookup_choices=[
            ("contains", "Contains (case-sensitive)"),
            ("icontains", "Contains (case-insensitive)"),
            ("exact", "Exact"),
        ]
    )
    protocol_name = filters.CharFilter("protocol_name", lookup_expr="contains")
    scanning_sequence = filters.MultipleChoiceFilter(
        "scanning_sequence",
        choices=ScanningSequence.choices(),
        conjoined=True,
        method=filter_array,
    )
    sequence_variant = filters.MultipleChoiceFilter(
        "sequence_variant",
        choices=SequenceVariant.choices(),
        conjoined=True,
        method=filter_array,
    )
    flip_angle = filters.AllValuesFilter("flip_angle")
    created_after_date = filters.DateFilter("date", lookup_expr="gte")
    date = filters.DateFilter("date")
    created_before_date = filters.DateFilter("date", lookup_expr="lte")
    created_after_time = filters.TimeFilter("time", lookup_expr="gte")
    created_before_time = filters.TimeFilter("time", lookup_expr="lte")
    manufacturer = filters.AllValuesFilter("manufacturer")
    manufacturer_model_name = filters.AllValuesFilter("manufacturer_model_name")
    magnetic_field_strength = filters.AllValuesFilter("magnetic_field_strength")
    device_serial_number = filters.AllValuesFilter("device_serial_number")
    institution_name = filters.AllValuesFilter("institution_name")

    class Meta:
        model = Series
        fields = (
            "id",
            "uid",
            "patient_id",
            "study_uid",
            "study_description",
            "modality",
            "description",
            "protocol_name",
            "number",
            "created_after_date",
            "created_before_date",
            "created_after_time",
            "created_before_time",
            "echo_time",
            "inversion_time",
            "repetition_time",
            "scanning_sequence",
            "sequence_variant",
            "flip_angle",
            "manufacturer",
            "manufacturer_model_name",
            "magnetic_field_strength",
            "device_serial_number",
            "institution_name",
            "patient__id",
        )
