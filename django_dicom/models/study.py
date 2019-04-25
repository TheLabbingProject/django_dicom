from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.validators import digits_and_dots_only


class Study(DicomEntity):
    """
    A model to represent DICOM_'s `study entity`_. Holds the corresponding
    attributes as discovered in created :class:`django_dicom.Image` instances.

    .. _DICOM: https://www.dicomstandard.org/
    .. _study entity: http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html
    
    """

    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Study UID",
    )
    description = models.CharField(max_length=64, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    FIELD_TO_HEADER = {
        "uid": "StudyInstanceUID",
        "date": "StudyDate",
        "time": "StudyTime",
        "description": "StudyDescription",
    }

    class Meta:
        verbose_name_plural = "Studies"
        indexes = [models.Index(fields=["uid"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self):
        return reverse("dicom:study_detail", args=[str(self.id)])
