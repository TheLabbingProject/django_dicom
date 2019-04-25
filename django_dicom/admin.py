from django.contrib import admin
from django_dicom.models import Image, Series, Study, Patient


class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "series", "number", "date", "time")
    ordering = ["-date", "-series", "number"]
    readonly_fields = ["uid"]


class ImageInLine(admin.TabularInline):
    model = Image
    exclude = ("uid", "date", "time")
    ordering = ["number"]


class SeriesAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "date", "time", "number", "description")
    ordering = ["-date", "-time"]
    inlines = (ImageInLine,)
    readonly_fields = ["uid"]


class SeriesInLine(admin.TabularInline):
    model = Series
    fields = (
        "date",
        "number",
        "description",
        "scanning_sequence",
        "sequence_variant",
        "repetition_time",
        "echo_time",
        "inversion_time",
    )
    ordering = ["date", "number"]


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
    list_display = ("id", "uid", "description")
    inlines = (StudySeriesInLine,)
    readonly_fields = ["uid"]


class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "given_name", "family_name", "sex", "date_of_birth")
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


admin.site.register(Image, ImageAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Patient, PatientAdmin)
