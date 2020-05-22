# from django_dicom.models.image import Image
# from django_mri.utils import get_dicom_root
# from io import BufferedReader
# from pathlib import Path

# DICOM_ROOT = get_dicom_root()


# class ImportImage:
#     # @classmethod
#     # def get_default_destination(cls, image: Image) -> Path:
#     #     relative_path = image.instance.default_relative_path
#     #     return DICOM_ROOT / relative_path

#     # @classmethod
#     # def move_image_to_destination(cls, image: Image, target: Path = None):
#     #     target = target or cls.get_default_destination(image)
#     #     image.rename(target)

#     # @classmethod
#     # def get_or_create_image(cls, path: Path) -> tuple:
#     #     try:
#     #         return Image.objects.get_or_create(dcm=path)
#     #     except Exception:
#     #         path.unlink()
#     #         raise

#     # @classmethod
#     # def from_buffer(cls, data: BufferedReader) -> tuple:
#     #     local_path = Image.objects.store_image_data(data)
#     #     image, created = cls.get_or_create_image(local_path)
#     #     if created:
#     #         cls.move_image_to_destination(image)
#     #     else:
#     #         local_path.unlink()
#     #     return image, created

#     # @classmethod
#     # def from_path(cls, path: Path) -> tuple:
#     #     with open(path, "rb") as data:
#     #         return cls.from_buffer(data)
