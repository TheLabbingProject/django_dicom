from django.db import models

# from django_dicom.reader.code_strings import ScanningSequence


class SeriesManager(models.Manager):
    pass

    # All of these methods are supposed to be utility methods to facilitate
    # querying. I'm not entirely sure they should be here or be at all.

    # def get_anatomicals(self, by_date: bool = False):
    #     anatomicals = self.filter(
    #         scanning_sequence=[ScanningSequence.GR.name, ScanningSequence.IR.name]
    #     ).order_by("date", "time")
    #     if by_date:
    #         dates = anatomicals.values_list("date", flat=True).distinct()
    #         return {date: anatomicals.filter(date=date) for date in dates}
    #     return anatomicals

    # def get_default_anatomical(self):
    #     return (
    #         self.get_anatomicals(by_date=False)
    #         .order_by("-date", "pixel_spacing__0", "pixel_spacing__1")
    #         .first()
    #     )

    # def get_anatomicals_by_pixel_spacing(self, pixel_spacing: list):
    #     return (
    #         self.get_anatomicals()
    #         .filter(pixel_spacing=pixel_spacing)
    #         .order_by("-date", "description")
    #     )

    # def get_inversion_recovery(self, by_date: bool = False):
    #     inversion_recovery = self.filter(
    #         scanning_sequence=[
    #             ScanningSequence.ECHO_PLANAR.name,
    #             ScanningSequence.INVERSION_RECOVERY.name,
    #         ],
    #         repetition_time__gt=6000,
    #     )
    #     if by_date:
    #         dates = inversion_recovery.values_list("date", flat=True).distinct()
    #         return {date: inversion_recovery.filter(date=date) for date in dates}
    #     return inversion_recovery

    # def get_latest_inversion_recovery_sequence(self):
    #     return self.get_inversion_recovery(by_date=False).order_by(
    #         "-date", "inversion_time"
    #     )
