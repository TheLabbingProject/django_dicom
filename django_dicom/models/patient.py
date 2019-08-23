from django.conf import settings
from django.db import models
from django.urls import reverse
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

    uid = models.CharField(max_length=64, unique=True, verbose_name="Patient UID")
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=Sex.choices(), blank=True, null=True)

    # Name parts as they are called in DICOM headers
    given_name = models.CharField(max_length=64, blank=True, null=True)
    family_name = models.CharField(max_length=64, blank=True, null=True)
    middle_name = models.CharField(max_length=64, blank=True, null=True)
    name_prefix = models.CharField(max_length=64, blank=True, null=True)
    name_suffix = models.CharField(max_length=64, blank=True, null=True)

    if hasattr(settings, "SUBJECT_MODEL"):
        subject = models.ForeignKey(
            settings.SUBJECT_MODEL,
            on_delete=models.PROTECT,
            related_name="dicom_patient_set",
            blank=True,
            null=True,
        )

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

    class Meta:
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date_of_birth"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:patient_detail", args=[str(self.id)])

    def get_full_name(self) -> str:
        """
        Returns the first and last names of the patient.
        
        Returns
        -------
        str
            Patient's first and last names.
        """

        return f"{self.given_name} {self.family_name}"

    def update_patient_name(self, header: HeaderInformation) -> None:
        """
        Parses the patient's name from the DICOM header and updates the instance's
        fields.
        
        Parameters
        ----------
        header : :class:`~django_dicom.reader.header_information.HeaderInformation`
            A DICOM image's :class:`~django_dicom.reader.header_information.HeaderInformation` instance.
        """

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
