"""
Definition of the :class:`FilterSet` subclass that will be assigned to the
:class:`~django_dicom.views.series.SeriesViewSet`\'s
:attr:`~django_dicom.views.series.SeriesViewSet.filter_class` attribute value.
"""

import json
import operator
from functools import reduce

from dicom_parser.utils.code_strings import (Modality, ScanningSequence,
                                             SequenceVariant)
from django.db.models import Q, QuerySet
from django_dicom.models.series import Series
from django_dicom.utils import utils, validation
from django_filters import rest_framework as filters


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


def filter_array(queryset: QuerySet, field_name: str, value: list):
    """
    Returns an exact lookup for a PostgreSQL ArrayField_.

    .. _ArrayField: https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/#arrayfield

    Parameters
    ----------
    queryset : :class:`~django.db.models.QuerySet`
        The filtered queryset
    field_name : str
        The name of the field the queryset is being filtered by
    value : list
        The values to filter by
    """

    if not value:
        return queryset
    # We check both content and length in order to return only exact matches
    contains = f"{field_name}__contains"
    length = f"{field_name}__len"
    kwargs = {contains: value, length: len(value)}
    return queryset.filter(**kwargs).all()


def filter_header(queryset: QuerySet, field_name: str, values: str):
    """
    Returns a desired lookup for a DicomHeader field.

    Parameters
    ----------
    queryset : :class:`~django.db.models.QuerySet`
        The filtered queryset
    field_name : str
        The name of the field the queryset is being filtered by
    values : dict
        The fields and values to filter by
    """

    if not values:
        return queryset

    series_all = queryset.all()
    values_json = json.loads(values)
    series_ids = []
    for series in series_all:
        header = series.image_set.first().header.instance
        result = validation.run_checks(values_json, header)
        if result:
            series_ids.append(series.id)

    return queryset.filter(id__in=series_ids).all()


def filter_in_string(queryset: QuerySet, field_name: str, values: list):
    """
    Returns a in-icontains mixed lookup with 'or' between values for a CharField.

    Parameters
    ----------
    queryset : :class:`~django.db.models.QuerySet`
        The filtered queryset
    field_name : str
        The name of the field the queryset is being filtered by
    values : str
        The values to filter by
    """

    if not values:
        return queryset
    # We check both content and length in order to return only exact matches
    icontains = f"{field_name}__icontains"
    condition = reduce(
        operator.or_, [Q(**{icontains: value}) for value in values]
    )
    return queryset.filter(condition).all()


class SeriesFilter(filters.FilterSet):
    """
    Provides filtering functionality for the
    :class:`~django_dicom.views.series.SeriesViewSet`.

    Available filters are:

        * *id*: Primary key
        * *uid*: Series Instance UID
        * *patient_id*: Related :class:`~django_dicom.models.patient.Patient`
          instance's primary key
        * *study_uid*: Related :class:`~django_dicom.models.study.Study`
          instance's :attr:`~django_dicom.models.study.Study.uid` value
        * *study_description*: Related
          :class:`~django_dicom.models.study.Study` instance's
          :attr:`~django_dicom.models.study.Study.description` value (in-icontains)
        * *modality*: Any of the values defined in
          :class:`~dicom_parser.utils.code_strings.modality.Modality`
        * *description*: Series description value (contains, icontains, or
          exact)
        * *number*: Series number value
        * *protocol_name*: Protocol name value (contains)
        * *scanning_sequence*: Any combination of the values defined in
          :class:`~dicom_parser.utils.code_strings.scanning_sequence.ScanningSequence`
        * *sequence_variant*: Any combination of the values defined in
          :class:`~dicom_parser.utils.code_strings.sequence_variant.SequenceVariant`
        * *echo_time*: :attr:`~django_dicom.models.series.Series.echo_time`
          value
        * *inversion_time*:
          :attr:`~django_dicom.models.series.Series.inversion_time` value
        * *repetition_time*:
          :attr:`~django_dicom.models.series.Series.repetition_time` value
        * *flip_angle*: Any of the existing
          :attr:`~django_dicom.models.series.Series.flip_angle` in the database
        * *created_after_date*: Create after date
        * *date*: Exact :attr:`~django_dicom.models.series.Series.date` value
        * *created_before_date*: Create before date
        * *created_after_time*: Create after time
        * *created_before_time*: Create before time
        * *manufacturer*: Any of the existing
          :attr:`~django_dicom.models.series.Series.manufacturer` in the database
        * *manufacturer_model_name*: Any of the existing
          :attr:`~django_dicom.models.series.Series.manufacturer_model_name` in
          the database
        * *device_serial_number*: Any of the existing
          :attr:`~django_dicom.models.series.Series.device_serial_number` in
          the database
        * *institution_name*: Any of the existing
          :attr:`~django_dicom.models.series.Series.institution_name` in the
          database
        * *pulse_sequence_name*:
          :attr:`~django_dicom.models.series.Series.pulse_sequence_name` value
          (in-icontains)
        * *sequence_name*:
          :attr:`~django_dicom.models.series.Series.sequence_name` value
          (in-icontains)
    """

    study_uid = filters.CharFilter(
        "study__uid", lookup_expr="exact", label="Study UID"
    )
    study_description = CharInFilter(
        field_name="study__description",
        lookup_expr="in",
        label="Study description icontains",
        method=filter_in_string,
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
    manufacturer_model_name = filters.AllValuesFilter(
        "manufacturer_model_name"
    )
    magnetic_field_strength = filters.AllValuesFilter(
        "magnetic_field_strength"
    )
    device_serial_number = filters.AllValuesFilter("device_serial_number")
    institution_name = filters.AllValuesFilter("institution_name")
    pulse_sequence_name = CharInFilter(
        field_name="pulse_sequence_name",
        lookup_expr="icontains",
        method=filter_in_string,
    )
    sequence_name = CharInFilter(
        field_name="sequence_name",
        lookup_expr="icontains",
        method=filter_in_string,
    )
    pixel_spacing = filters.RangeFilter("pixel_spacing__0")
    slice_thickness = filters.RangeFilter("slice_thickness")
    repetition_time = filters.RangeFilter("repetition_time")
    inversion_time = filters.RangeFilter("inversion_time")
    echo_time = filters.RangeFilter("echo_time")
    header_fields = filters.CharFilter("image", method=filter_header)

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
            "slice_thickness",
            "pixel_spacing",
            "scanning_sequence",
            "sequence_variant",
            "flip_angle",
            "manufacturer",
            "manufacturer_model_name",
            "magnetic_field_strength",
            "device_serial_number",
            "institution_name",
            "patient__id",
            "pulse_sequence_name",
            "sequence_name",
        )
