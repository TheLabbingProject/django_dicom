from django.db import models
from django.urls import reverse
from django_dicom.models import Instance
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers import StudyManager
from django_dicom.models.validators import digits_and_dots_only


class Study(DicomEntity):
    study_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Study UID",
    )
    description = models.CharField(max_length=64)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    is_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = StudyManager()

    FIELD_TO_HEADER = {
        "study_uid": "StudyInstanceUID",
        "date": "StudyDate",
        "time": "StudyTime",
        "description": "StudyDescription",
    }

    def __str__(self):
        return self.study_uid

    def get_absolute_url(self):
        return reverse("dicom:study_detail", args=[str(self.id)])

    def get_latest_instance(self):
        return self.instance_set.order_by("-created_at").first()

    def get_latest_header_value(self, tag_or_keyword):
        latest_instance = self.get_latest_instance()
        if latest_instance:
            return latest_instance.get_header_value(tag_or_keyword)
        return None

    def update_fields_from_header(self, force=False):
        for field in self.get_model_header_fields():
            not_null = getattr(self, field.name, False)
            if not force and not_null:
                continue
            header_name = self.FIELD_TO_HEADER.get(field.name)
            if header_name:
                latest_value = self.get_latest_header_value(header_name)
                if latest_value:
                    setattr(self, field.name, latest_value)
        self.is_updated = True

    class Meta:
        verbose_name_plural = "Studies"
        indexes = [models.Index(fields=["study_uid"])]

    @property
    def has_series(self):
        return bool(self.series_set.count())

    @property
    def instance_set(self):
        return Instance.objects.filter(series__in=self.series_set.all())

