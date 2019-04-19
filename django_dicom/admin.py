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


class StudyAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "description")
    inlines = (SeriesInLine,)
    readonly_fields = ["uid"]


class PatientInLine(admin.StackedInline):
    model = Patient
    verbose_name_plural = "MRI"
    fields = ("studies", "series_count", "dicom_count")
    readonly_fields = ("studies", "series_count", "dicom_count")

    def get_series(self, instance):
        return Series.objects.filter(patient=instance)

    def series_count(self, instance):
        return self.get_series(instance).count()

    def get_studies(self, instance):
        return Study.objects.filter(
            id__in=self.get_series(instance).values("study").distinct()
        )

    def get_study_list(self, instance):
        return self.get_studies(instance).values_list("description")

    def studies(self, instance):
        return [study for study in self.get_study_list(instance)]

    def dicom_count(self, instance):
        return Image.objects.filter(patient=instance).count()

    dicom_count.short_description = "DICOM files"


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
        ("Associated Model", {"fields": ("subject",)}),
    )


admin.site.register(Image, ImageAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Patient, PatientAdmin)
