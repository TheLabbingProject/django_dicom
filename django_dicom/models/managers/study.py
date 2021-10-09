from django.db.models import Count, QuerySet


class StudyQuerySet(QuerySet):
    def with_counts(self):
        return self.annotate(
            n_patients=Count("series__patient", distinct=True),
            n_series=Count("series", distinct=True),
            n_images=Count("series__image"),
        )
