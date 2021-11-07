from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe

from django_dicom.models.data_element import DataElement
from django_dicom.models.data_element_definition import DataElementDefinition
from django_dicom.models.header import Header
from django_dicom.models.image import Image
from django_dicom.models.networking import StorageServiceClassProvider
from django_dicom.models.networking.status import ServerStatus
from django_dicom.models.patient import Patient
from django_dicom.models.series import Series
from django_dicom.models.study import Study
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.models.values.sequence_of_items import SequenceOfItems
from django_dicom.utils.html import Html

SERVER_STATUS_COLOR = {
    ServerStatus.UP: "green",
    ServerStatus.INACTIVE: "orange",
    ServerStatus.DOWN: "red",
}
SERVER_STATUS_INDICATOR = (
    '<div style="color: {color}; font-size: 40px;">&bull;</div>'
)


class DataElementInLine(admin.TabularInline):
    model = DataElement
    fields = (
        "id_link",
        "definition_tag",
        "definition_keyword",
        "VR",
        "VM",
        "value",
    )
    readonly_fields = (
        "id_link",
        "definition_tag",
        "definition_keyword",
        "VR",
        "VM",
        "value",
    )
    ordering = ["definition__keyword"]
    extra = 0

    def definition_tag(self, data_element: DataElement) -> str:
        return data_element.definition.admin_link

    def definition_keyword(self, data_element: DataElement) -> str:
        return data_element.definition.keyword

    def id_link(self, data_element: DataElement) -> str:
        return data_element.admin_link

    def value(self, data_element: DataElement):
        html = data_element.to_html(verbose=False)
        if html:
            return html
        return "" if data_element.value is None else data_element.value

    def VR(self, data_element: DataElement) -> str:
        return data_element.definition.value_representation

    def VM(self, data_element: DataElement) -> str:
        return data_element.value_multiplicity

    definition_keyword.short_description = "Keyword"
    definition_tag.short_description = "Tag"
    id_link.short_description = "ID"


class DataElementDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "tag",
        "keyword",
        "value_representation",
        "description",
    )
    ordering = ["keyword"]
    search_fields = ("tag", "keyword")


class DataElementValueAdmin(admin.ModelAdmin):
    fields = "id", "index", "raw", "_value", "warnings"
    readonly_fields = "id", "index", "raw", "_value"
    list_display = (
        "id",
        "index",
        "_raw_peek",
        "_value_link",
        "warnings",
    )
    ordering = ["id"]

    def _raw_peek(self, data_element_value: DataElementValue) -> str:
        return data_element_value.get_raw_peek()

    def _value(self, data_element_value: DataElementValue) -> str:
        verbose = not isinstance(data_element_value, SequenceOfItems)
        return data_element_value.to_html(verbose=verbose)

    def _value_link(self, data_element_value: DataElementValue):
        return data_element_value.to_html(verbose=False)

    _raw_peek.short_description = "Raw"
    _value.short_description = "Value"
    _value_link.short_description = "Value"

    def get_queryset(self, request) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.select_subclasses()


class DataElementAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "header_link",
        "definition_tag",
        "definition_keyword",
        "value_representation",
        "value",
        "value_instances",
    )
    readonly_fields = (
        "id",
        "header_link",
        "definition_tag",
        "definition_keyword",
        "value_representation",
        "value",
        "value_instances",
    )
    list_display = (
        "id",
        "header_link",
        "definition_tag",
        "definition_keyword",
        "value_representation",
        "value",
    )
    list_filter = (
        "definition__keyword",
        "definition__value_representation",
    )
    ordering = ("definition__keyword",)

    def tag(self, data_element: DataElement):
        return data_element.definition.tag

    def definition_tag(self, data_element) -> tuple:
        return data_element.definition.admin_link

    def definition_keyword(self, data_element) -> tuple:
        return data_element.definition.keyword

    def header_link(self, data_element: DataElement):
        return data_element.header.admin_link

    def value_instances(self, data_element: DataElement):
        values = data_element._values.all()
        links = [value.admin_link for value in values]
        return Html.break_html(links)

    def value_representation(self, data_element: DataElement):
        return data_element.definition.get_value_representation_display()

    definition_keyword.short_description = "Keyword"
    definition_tag.short_description = "Tag"
    header_link.short_description = "Header"


class HeaderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient_link",
        "series_link",
        "image_link",
        "parent_link",
    )
    ordering = ("-id",)
    readonly_fields = (
        "id",
        "patient_link",
        "series_link",
        "image_link",
        "parent_link",
        "index",
    )
    inlines = (DataElementInLine,)

    class Media:
        css = {"all": ("django_dicom/css/hide_admin_original.css",)}

    def patient_link(self, header: Header):
        return header.image.series.patient.admin_link

    def series_link(self, header: Header):
        return header.image.series.admin_link

    def image_link(self, header: Header):
        return header.image.admin_link

    def parent_link(self, header: Header):
        if header.parent:
            return header.parent.admin_link

    parent_link.short_description = "Parent"
    image_link.short_description = "Image"
    series_link.short_description = "Series"
    patient_link.short_description = "Patient"


class ImageAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "dcm",
        "uid",
        "series_link",
        "series_description",
        "number",
        "date",
        "time",
        "header_link",
        "warnings",
    )
    list_display = (
        "id",
        "uid",
        "header_link",
        "date",
        "time",
        "series_link",
        "number",
    )
    ordering = "-date", "-time", "-series", "number"
    readonly_fields = (
        "id",
        "dcm",
        "uid",
        "series_link",
        "series_description",
        "number",
        "date",
        "time",
        "header_link",
        "warnings",
    )

    def header_link(self, image: Image):
        return image.header.admin_link

    def series_link(self, image: Image):
        return image.series.admin_link

    def series_description(self, image: Image):
        return image.series.description

    header_link.short_description = "Header"
    series_description.short_description = "Series Description"
    series_link.short_description = "Series"


class ImageInLine(admin.TabularInline):
    model = Image
    fields = "id_link", "number", "dcm", "header_link", "warnings"
    ordering = ("number",)
    readonly_fields = "id_link", "number", "dcm", "header_link", "warnings"
    extra = 0

    class Media:
        css = {"all": ("django_dicom/css/hide_admin_original.css",)}

    def header_link(self, image: Image):
        return image.header.admin_link

    def id_link(self, image: Image) -> str:
        return image.admin_link

    header_link.short_description = "Header"
    id_link.short_description = "ID"


class SeriesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient_link",
        "date",
        "time",
        "number",
        "description",
        "sequence_type",
        "uid",
    )
    inlines = (ImageInLine,)
    readonly_fields = ("uid",)
    list_filter = "date", "sequence_type"
    search_fields = "description", "uid", "patient__uid"

    def patient_link(self, series: Header):
        return series.patient.admin_link

    patient_link.short_description = "Patient"


class SeriesInLine(admin.TabularInline):
    model = Series
    fields = (
        "id_link",
        "institution_name",
        "modality",
        "manufacturer",
        "manufacturer_model_name",
        "date",
        "time",
        "number",
        "description",
        "body_part_examined",
        "_scanning_sequence",
        "_sequence_variant",
        "repetition_time",
        "echo_time",
        "inversion_time",
        "_spatial_resolution",
        "_images",
    )
    readonly_fields = (
        "id_link",
        "institution_name",
        "modality",
        "manufacturer",
        "manufacturer_model_name",
        "date",
        "time",
        "number",
        "description",
        "body_part_examined",
        "_scanning_sequence",
        "_sequence_variant",
        "repetition_time",
        "echo_time",
        "inversion_time",
        "_spatial_resolution",
        "_images",
    )
    ordering = ["-date", "number"]
    extra = 0

    def id_link(self, series: Series) -> str:
        return Html.admin_link("Series", series.id)

    def _scanning_sequence(self, series: Series) -> str:
        sequences = series.get_scanning_sequence_display()
        if sequences:
            return "\n".join([f"• {sequence}" for sequence in sequences])

    def _sequence_variant(self, series: Series) -> str:
        variants = series.get_sequence_variant_display()
        if variants:
            return "\n".join([f"• {variant}" for variant in variants])

    def _spatial_resolution(self, series: Series) -> tuple:
        spatial_resolution = series.spatial_resolution
        if spatial_resolution:
            return tuple([round(number, 2) for number in spatial_resolution])

    def _images(self, series: Series) -> int:
        return series.image_set.count()

    id_link.short_description = "ID"


class StudySeriesInLine(admin.TabularInline):
    model = Series
    fields = (
        "patient",
        "date",
        "number",
        "description",
        "scanning_sequence",
        "sequence_variant",
    )
    ordering = ["patient", "date", "number"]


class StudyAdmin(admin.ModelAdmin):
    list_display = "id", "uid", "description"
    inlines = (StudySeriesInLine,)
    readonly_fields = ["uid"]


class StorageServiceClassProviderAdmin(admin.ModelAdmin):
    list_display = "title", "_ip", "port", "_status"

    def _ip(self, instance: StorageServiceClassProvider) -> str:
        return instance.ip or "0.0.0.0"

    def _status(self, instance: StorageServiceClassProvider) -> str:
        color = SERVER_STATUS_COLOR.get(instance.status)
        html = SERVER_STATUS_INDICATOR.format(color=color)
        return mark_safe(html)


class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uid",
        "given_name",
        "family_name",
        "sex",
        "date_of_birth",
    )
    inlines = (SeriesInLine,)
    fieldsets = (
        (None, {"fields": ("uid",)}),
        (
            "Name",
            {
                "fields": (
                    "name_prefix",
                    "given_name",
                    "middle_name",
                    "family_name",
                    "name_suffix",
                )
            },
        ),
        ("Personal Information", {"fields": ("sex", "date_of_birth")}),
    )


admin.site.register(DataElementDefinition, DataElementDefinitionAdmin)
admin.site.register(DataElementValue, DataElementValueAdmin)
admin.site.register(DataElement, DataElementAdmin)
admin.site.register(Header, HeaderAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(
    StorageServiceClassProvider, StorageServiceClassProviderAdmin
)
