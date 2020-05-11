# from django_dicom.models.image import Image
# from django_dicom.data_import.import_image import ImportImage
# from django_dicom.data_import.utils.progressbar import create_progressbar
# from pathlib import Path


# class LocalImport:
#     @classmethod
#     def from_path(cls, path: Path) -> tuple:
#         image_ids = []
#         any_created = False
#         progressbar = create_progressbar(path.rglob("*.dcm"), unit="image")
#         for dcm_path in progressbar:
#             image, created = ImportImage.from_path(dcm_path)
#             any_created = any_created or created
#             image_ids.append(image.id)
#         images = Image.objects.filter(id__in=image_ids)
#         return images, any_created
