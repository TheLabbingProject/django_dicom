import numpy as np
import os
import pydicom
import shutil

from django.conf import settings
from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers import InstanceManager
from django_dicom.models.validators import digits_and_dots_only
from django_dicom.models.value_representation import parse_element


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
    created_at = models.DateTimeField(auto_now_add=True)

    series = models.ForeignKey(
        "django_dicom.Series", blank=True, null=True, on_delete=models.PROTECT
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

    def read_file(self) -> pydicom.dataset.FileDataset:
        return pydicom.read_file(self.file.path)

    def get_data(self) -> np.ndarray:
        return self.read_file().pixel_array

    def read_headers(self) -> pydicom.dataset.FileDataset:
        return pydicom.dcmread(self.file.path, stop_before_pixels=True)

    def get_header_element_by_keyword(
        self, keyword: str
    ) -> pydicom.dataelem.DataElement:
        try:
            return self.headers.data_element(keyword)
        except KeyError:
            return None

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

    def get_header_value(self, tag_or_keyword, parsed: bool = True):
        if parsed:
            return self.get_parsed_header_value(tag_or_keyword)
        return self.get_raw_header_value(tag_or_keyword)

    def update_fields_from_header(self, force: bool = False):
        for field in self.get_model_header_fields():
            if not force and getattr(self, field.name, False):
                continue
            header_name = self.FIELD_TO_HEADER.get(field.name)
            if header_name:
                value = self.get_header_value(header_name)
                if value:
                    setattr(self, field.name, value)

    def get_default_file_name(self) -> str:
        return f"{self.number}.dcm"

    def get_default_relative_path(self) -> str:
        patient_id = self.get_header_value("PatientID")
        series_uid = self.get_header_value("SeriesInstanceUID")
        name = self.get_default_file_name()
        return os.path.join("MRI", patient_id, series_uid, "DICOM", name)

    def get_entity_uid_from_headers(self, model: DicomEntity) -> str:
        field_name = model.objects.UID_FIELD
        header_key = model.FIELD_TO_HEADER.get(field_name)
        return self.get_header_value(header_key)

    def get_or_create_by_uid(self, model: DicomEntity) -> DicomEntity:
        entity_uid = self.get_entity_uid_from_headers(model)
        return model.objects.get_or_create_by_uid(entity_uid)

    def move_file(self, relative_destination: str = None) -> str:
        relative_destination = relative_destination or self.get_default_relative_path()
        destination = os.path.join(settings.MEDIA_ROOT, relative_destination)
        current_path = self.file.path
        self.file.name = relative_destination
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        os.rename(current_path, destination)
        return destination

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

    @property
    def patient(self):
        try:
            return self.series.patient
        except AttributeError:
            return None

    @property
    def study(self):
        try:
            return self.series.study
        except AttributeError:
            return None

    class Meta:
        indexes = [
            models.Index(fields=["instance_uid"]),
            models.Index(fields=["date", "time"]),
        ]

