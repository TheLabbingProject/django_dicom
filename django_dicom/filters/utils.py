"""
Utilities for the :mod:`django_dicom.filters` module.
"""
from django_filters import rest_framework as filters


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


DEFAULT_LOOKUP_CHOICES = (
    ("contains", "Contains (case-sensitive)"),
    ("icontains", "Contains (case-insensitive)"),
    ("exact", "Exact"),
)
