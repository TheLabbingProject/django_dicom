"""
Definition of the :class:`PatientQuerySet` class.
"""
from django.db.models import (
    Count,
    QuerySet,
    Subquery,
    F,
    OuterRef,
    ExpressionWrapper,
    DateTimeField,
)
from django.apps import apps


STUDY_DATETIME_ANNOTATION = ExpressionWrapper(
    F("date") + F("time"), output_field=DateTimeField()
)


class PatientQuerySet(QuerySet):
    def with_latest_study_time(self) -> QuerySet:
        Study = apps.get_model("django_dicom.Study")
        studies = (
            Study.objects.filter(series__patient=OuterRef("pk"))
            .annotate(datetime=STUDY_DATETIME_ANNOTATION)
            .order_by("-datetime")
        )
        return self.annotate(
            latest_study_time=Subquery(studies.values("datetime")[:1])
        )

    def with_counts(self) -> QuerySet:
        return self.annotate(
            n_studies=Count("series__study", distinct=True),
            n_series=Count("series", distinct=True),
            n_images=Count("series__image"),
        )
