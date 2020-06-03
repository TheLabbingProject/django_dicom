from dicom_parser.header import Header as DicomHeader
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.managers.header import HeaderManager
from django_dicom.models.patient import Patient
from django_dicom.models.series import Series
from django_dicom.models.study import Study
from django_dicom.utils.html import Html
from model_utils.models import TimeStampedModel


class Header(TimeStampedModel):
    parent = models.ForeignKey(
        "django_dicom.SequenceOfItems", on_delete=models.CASCADE, blank=True, null=True
    )
    index = models.PositiveIntegerField(blank=True, null=True)

    _instance = None

    objects = HeaderManager()

    def to_verbose_list(self) -> list:
        return [
            data_element.to_verbose_dict()
            for data_element in self.data_element_set.all()
        ]

    def to_html(self, verbose: bool = False, **kwargs) -> str:
        if verbose:
            return Html.json(self.to_verbose_list())
        text = f"Header #{self.id}"
        return Html.admin_link("Header", self.id, text)

    def get_value_by_keyword(self, keyword: str):
        try:
            data_element = self.data_element_set.get(definition__keyword=keyword)
        except ObjectDoesNotExist:
            return None
        else:
            return data_element.value

    def get_entity_uid(self, entity: DicomEntity) -> str:
        keyword = entity.get_header_keyword("uid")
        return self.instance.get(keyword)

    def get_or_create_entity(self, entity: DicomEntity) -> tuple:
        return entity.objects.from_header(self)

    def get_or_create_series(self) -> tuple:
        return self.get_or_create_entity(Series)

    def get_or_create_patient(self) -> tuple:
        return self.get_or_create_entity(Patient)

    def get_or_create_study(self) -> tuple:
        return self.get_or_create_entity(Study)

    @property
    def instance(self) -> DicomHeader:
        if not isinstance(self._instance, DicomHeader):
            self._instance = DicomHeader(self.image.dcm.path)
        return self._instance

    @property
    def admin_link(self) -> str:
        model_name = self.__class__.__name__
        return Html.admin_link(model_name, self.id)
