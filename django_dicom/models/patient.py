import numpy as np

from django.db import models
from django.urls import reverse
from django_dicom.models import Image
from django_dicom.reader.code_strings import Sex
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.reader import HeaderInformation


class Patient(DicomEntity):
    """
    A model to represent DICOM_'s `patient entity`_. Holds the corresponding
    attributes as discovered in created :class:`django_dicom.Image` instances.

    .. _DICOM: https://www.dicomstandard.org/
    .. _patient entity: http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html
    
    """

    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=6, choices=Sex.choices(), blank=True, null=True)

    # Name parts as they are called in DICOM headers
    given_name = models.CharField(max_length=64, blank=True, null=True)
    family_name = models.CharField(max_length=64, blank=True, null=True)
    middle_name = models.CharField(max_length=64, blank=True, null=True)
    name_prefix = models.CharField(max_length=64, blank=True, null=True)
    name_suffix = models.CharField(max_length=64, blank=True, null=True)

    comments = models.TextField(max_length=1000, blank=True, null=True)

    # subject = models.ForeignKey(
    #     "research.Subject",
    #     blank=True,
    #     null=True,
    #     on_delete=models.PROTECT,
    #     related_name="mri_patient_set",
    # )

    FIELD_TO_HEADER = {
        "uid": "PatientID",
        "date_of_birth": "PatientBirthDate",
        "sex": "PatientSex",
    }
    NAME_PARTS = [
        "given_name",
        "family_name",
        "middle_name",
        "name_prefix",
        "name_suffix",
    ]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:patient_detail", args=[str(self.id)])

    def get_full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"

    def update_patient_name(self, header: HeaderInformation) -> None:
        value = header.get_raw_value("PatientName")
        for part in self.NAME_PARTS:
            part_value = getattr(value, part, None)
            if part_value:
                setattr(self, part, part_value)

    def update_fields_from_header(
        self, header: HeaderInformation, exclude: list = []
    ) -> None:
        """
        Override :class:`django_dicom.DicomEntity`'s :meth:`django_dicom.DicomEntity.update_fields_from_header`
        in order to handle setting the name parts seperately.
        
        Parameters
        ----------
        header : HeaderInformation
            DICOM header data.
        exclude : list, optional
            Field names to exclude (the default is [], which will not exclude any header fields).
        """

        exclude += self.NAME_PARTS
        super().update_fields_from_header(header, exclude=exclude)
        self.update_patient_name(header)

    def to_tree(self) -> list:
        return [series.to_tree_node() for series in self.series_set.all()]

    def get_anatomicals(self, by_date: bool = False):
        return self.series_set.get_anatomicals(by_date=by_date)

    def get_default_anatomical(self):
        return self.series_set.get_default_anatomical()

    def get_second_session_anatomical(self):
        anatomicals_by_date = self.series_set.get_anatomicals(by_date=True)
        if len(anatomicals_by_date) > 1:
            default = self.get_default_anatomical()
            del anatomicals_by_date[default.date]
            return (
                list(anatomicals_by_date.values())[0]
                .order_by("pixel_spacing__0", "pixel_spacing__1")
                .first()
            )

    def get_inversion_recovery(self):
        return self.series_set.get_inversion_recovery()

    def get_latest_inversion_recovery_sequence(self):
        return self.series_set.get_latest_inversion_recovery_sequence()

    def get_anatomicals_by_pixel_spacing(self, pixel_spacing: list):
        return self.series_set.get_anatomicals_by_pixel_spacing(pixel_spacing)

    def calculate_mutual_information(
        self, other, histogram_bins: int = 10
    ) -> np.float64:
        self_anatomical = self.get_default_anatomical()
        other_anatomical = other.get_default_anatomical()
        return self_anatomical.calculate_mutual_information(
            other_anatomical, histogram_bins
        )

    class Meta:
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date_of_birth"])]

    @property
    def has_series(self):
        return bool(self.series_set.count())

    @property
    def image_set(self):
        return Image.objects.filter(series__in=self.series_set.all())

