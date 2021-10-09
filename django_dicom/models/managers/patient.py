"""
Definition of the :class:`PatientQuerySet` class.
"""
from django.db.models import Count, QuerySet


class PatientQuerySet(QuerySet):
    def with_counts(self):
        return self.annotate(
            n_studies=Count("series__study", distinct=True),
            n_series=Count("series", distinct=True),
            n_images=Count("series__image"),
        )
