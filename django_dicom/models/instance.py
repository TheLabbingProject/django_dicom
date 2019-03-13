import array
import os
import pydicom
import shutil
import zipfile

from django.db.utils import IntegrityError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.patient import Patient
from django_dicom.models.series import Series
from django_dicom.models.study import Study
from django_dicom.models.validators import digits_and_dots_only
from django_dicom.models.value_representation import parse_element


class InstanceManager(models.Manager):
    def from_dcm(self, file):
        dest_name = default_storage.save("tmp.dcm", ContentFile(file.read()))
        instance = Instance()
        instance.file = dest_name
        try:
            instance.save()
        except IntegrityError:
            dest_path = os.path.join(settings.MEDIA_ROOT, dest_name)
            uid = pydicom.dcmread(dest_path).SOPInstanceUID
            os.remove(dest_path)
            return Instance.objects.filter(instance_uid=uid).first()
        return instance

    def from_zip(self, file):
        dest_name = default_storage.save("tmp.zip", ContentFile(file.read()))
        dest_path = os.path.join(settings.MEDIA_ROOT, dest_name)
        with zipfile.ZipFile(dest_path, "r") as archive:
            for file_name in archive.namelist():
                if file_name.endswith(".dcm"):
                    with archive.open(file_name) as dcm_file:
                        self.from_dcm(dcm_file)
        os.remove(dest_path)

    def from_local_directory(self, path: str):
        for directory, sub_directory, file_list in os.walk(path):
            for file_name in file_list:
                if file_name.endswith(".dcm"):
                    full_path = os.path.join(directory, file_name)
                    with open(full_path, "rb") as f:
                        self.from_dcm(f)


def fix_slice_timing(value: bytes) -> list:
    return [round(slice_time, 5) for slice_time in list(array.array("d", value))]


def fix_gradient_direction(value: bytes) -> list:
    return [float(value) for value in list(array.array("d", value))]


class Instance(DicomEntity):
    instance_uid = models.CharField(
        max_length=64,
        unique=True,
        blank=False,
        null=False,
        validators=[digits_and_dots_only],
        verbose_name="Instance UID",
    )
    file = models.FileField(upload_to="dicom", blank=True)
    number = models.IntegerField(blank=True, null=True, verbose_name="Instance Number")
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    b_value = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    series = models.ForeignKey(Series, blank=True, null=True, on_delete=models.PROTECT)
    study = models.ForeignKey(Study, blank=True, null=True, on_delete=models.PROTECT)
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.PROTECT
    )

    objects = InstanceManager()

    _headers = None
    FIELD_TO_HEADER = {
        "instance_uid": "SOPInstanceUID",
        "number": "InstanceNumber",
        "date": "InstanceCreationDate",
        "time": "InstanceCreationTime",
    }

    def __str__(self):
        return self.instance_uid

    def get_absolute_url(self):
        return reverse("dicom:instance_detail", args=[str(self.id)])

    def read_data(self) -> pydicom.dataset.FileDataset:
        return pydicom.dcmread(self.file.path)

    def read_headers(self) -> pydicom.dataset.FileDataset:
        return pydicom.dcmread(self.file.path, stop_before_pixels=True)

    def get_header_element_by_keyword(
        self, keyword: str
    ) -> pydicom.dataelem.DataElement:
        return self.headers.data_element(keyword)

    def get_header_element_by_tag(self, tag: tuple) -> pydicom.dataelem.DataElement:
        return self.headers.get(tag)

    def get_header_element(self, tag_or_keyword) -> pydicom.dataelem.DataElement:
        if type(tag_or_keyword) is str:
            return self.get_header_element_by_keyword(tag_or_keyword)
        elif type(tag_or_keyword) is tuple:
            return self.get_header_element_by_tag(tag_or_keyword)
        return None

    def get_raw_header_value(self, tag_or_keyword):
        element = self.get_header_element(tag_or_keyword)
        if element:
            return element.value
        return None

    def get_parsed_header_value(self, tag_or_keyword):
        element = self.get_header_element(tag_or_keyword)
        if element:
            return parse_element(element)
        return None

    def get_header_value(self, tag_or_keyword, parsed=True):
        if parsed:
            return self.get_parsed_header_value(tag_or_keyword)
        return self.get_raw_header_value(tag_or_keyword)

    # def get_series(self) -> Series:
    #     series_uid = self.get_header_value("SeriesInstanceUID")
    #     series, created = Series.objects.get_or_create(series_uid=series_uid)
    #     if created:
    #         series.update_fields_from_header()
    #     return Series.objects.get_or_create(series_uid=series_uid)[0]

    # def get_study_attributes(self) -> dict:
    #     return {
    #         "study_uid": self.headers.StudyInstanceUID,
    #         "date": self.parse_date_element(self.headers.StudyDate),
    #         "time": self.parse_time_element(self.headers.StudyTime),
    #         "description": self.headers.StudyDescription,
    #     }

    # def create_study(self) -> Study:
    #     return Study.objects.create(**self.get_study_attributes())

    # def get_study(self) -> Study:
    #     study_uid = self.headers.StudyInstanceUID
    #     study = Study.objects.filter(study_uid=study_uid).first()
    #     if not study:
    #         study = self.create_study()
    #     return study

    # def get_patient_attributes(self) -> dict:
    #     patient_name = self.get_header_value("PatientName")
    #     return {
    #         "patient_id": self.get_header_value("PatientID"),
    #         "given_name": patient_name.given_name,
    #         "family_name": patient_name.family_name,
    #         "middle_name": patient_name.middle_name,
    #         "name_prefix": patient_name.name_prefix,
    #         "name_suffix": patient_name.name_suffix,
    #         "date_of_birth": self.get_header_value("PatientBirthDate"),
    #         "sex": self.get_header_value("PatientSex"),
    #     }

    # def create_patient(self) -> Patient:
    #     return Patient.objects.create(**self.get_patient_attributes())

    # def get_patient(self) -> Patient:
    #     patient_id = self.headers.PatientID
    #     patient = Patient.objects.filter(patient_id=patient_id).first()
    #     if not patient:
    #         patient = self.create_patient()
    #     return patient

    # def get_attributes_from_file(self) -> dict:
    #     return {
    #         "instance_uid": self.headers.SOPInstanceUID,
    #         "number": int(self.headers.InstanceNumber),
    #         "date": self.parse_date_element(self.headers.InstanceCreationDate),
    #         "time": self.parse_time_element(self.headers.InstanceCreationTime),
    #         "series": self.get_series(),
    #         "study": self.get_study(),
    #         "patient": self.get_patient(),
    #     }

    # def update_attributes_from_file(self) -> None:
    #     attributes = self.get_attributes_from_file()
    #     for key, value in attributes.items():
    #         setattr(self, key, value)

    def update_fields_from_header(self, force=False):
        for field in self.get_model_header_fields():
            if not force and getattr(self, field.name, False):
                continue
            header_name = self.FIELD_TO_HEADER.get(field.name)
            if header_name:
                value = self.get_header_value(header_name)
                if value:
                    setattr(self, field.name, value)

    def get_or_create_series(self) -> Series:
        if not self.series:
            series, created = Series.objects.get_or_create(
                series_uid=self.headers.SeriesInstanceUID
            )
            self.series = series
            self.save()
            if created:
                series.update_fields_from_header(force=False)
                series.save()
        return self.series

    def get_or_create_patient(self) -> Patient:
        if not self.patient:
            patient, created = Patient.objects.get_or_create(
                patient_id=self.headers.PatientID
            )
            self.patient = patient
            self.save()
            if created:
                patient.update_fields_from_header(force=False)
                patient.save()
        return self.patient

    def get_or_create_study(self) -> Study:
        if not self.study:
            study, created = Study.objects.get_or_create(
                study_uid=self.headers.StudyInstanceUID
            )
            self.study = study
            self.save()
            if created:
                study.update_fields_from_header(force=False)
                study.save()
        return self.study

    def get_default_file_name(self) -> str:
        return os.path.join(
            "MRI",
            self.headers.PatientID,
            self.headers.SeriesInstanceUID,
            "DICOM",
            f"{self.number}.dcm",
        )

    def move_file(self, new_name: str = None) -> str:
        """
        Move the 'file' FileField attribute from its current location to
        another location relative to MEDIA_ROOT.

        :param new_name: New relative path, defaults to None (default path)
        :param new_name: str, optional
        :return:
        :rtype: None
        """
        new_name = new_name or self.get_default_file_name()
        initial_path = self.file.path
        self.file.name = new_name
        new_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(initial_path, new_path)
        return new_path

    def create_backup(self, dest: str):
        shutil.copyfile(self.file.path, dest)
        self.has_raw_backup = True
        self.save()

    def get_b_value(self) -> int:
        return self.get_header_value(("0019", "100c"))

    @property
    def headers(self) -> pydicom.dataset.FileDataset:
        if self._headers is None:
            self._headers = self.read_headers()
        return self._headers

    @property
    def slice_timing(self):
        return self.get_header_value(("0019", "1029"))

    @property
    def gradient_direction(self):
        return self.get_header_value(("0019", "100e"))
