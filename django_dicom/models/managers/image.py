from dicom_parser.header import Header as DicomHeader
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django_dicom.models.managers.dicom_entity import DicomEntityManager
from django_dicom.models.utils.progressbar import create_progressbar
from io import BufferedReader
from pathlib import Path


class ImageManager(DicomEntityManager):
    TEMP_DCM_FILE_NAME = "tmp.dcm"

    def store_image_data(self, image_data: BufferedReader) -> Path:
        content = ContentFile(image_data.read())
        relative_path = default_storage.save(self.TEMP_DCM_FILE_NAME, content)
        return Path(settings.MEDIA_ROOT, relative_path)

    def create_from_dcm(self, path: Path, autoremove: bool = True):
        try:
            return self.create(dcm=str(path))

        # In case the file is located outside MEDIA_ROOT (and therefore is
        # inaccessible), create an accessible copy and then initialize Image
        # instance.
        except SuspiciousFileOperation:
            with open(path, "rb") as data:
                local_path = self.store_image_data(data)
            return self.create(dcm=str(local_path))

        # If the creation failed, remove the local copy and re-raise the
        # exception.
        except Exception:
            if autoremove and path.is_file():
                path.unlink()
            raise

    def get_or_create_from_dcm(self, path: Path, autoremove: bool = True) -> tuple:
        header = DicomHeader(path)
        uid = header.get("SOPInstanceUID")
        try:
            existing = self.get(uid=uid)
        except ObjectDoesNotExist:
            new_instance = self.create_from_dcm(path, autoremove=autoremove)
            return new_instance, True
        else:
            return existing, False

    def get_or_create(self, *args, **kwargs) -> tuple:
        dcm_path = kwargs.get("dcm")
        if dcm_path:
            return self.get_or_create_from_dcm(Path(dcm_path))
        return super().get_or_create(*args, **kwargs)

    def report_import_path_results(self, path: Path, counter: dict) -> None:
        n_created, n_existing = counter.get("created"), counter.get("existing")
        if n_created or n_existing:
            print(f"\nSuccessfully imported DICOM data from {path}!")
            if n_created:
                print(f'Created:\t{counter["created"]}')
            if n_existing:
                print(f'Existing:\t{counter["existing"]}')
        else:
            print("\nNo .dcm files found!")

    def import_path(
        self, path: Path, progressbar: bool = True, report: bool = True
    ) -> dict:
        iterator = Path(path).rglob("*.dcm")
        # Create a progressbar wrapped iterator using tqdm
        if progressbar:
            iterator = create_progressbar(iterator, unit="image")
        if report:
            counter = {"created": 0, "existing": 0}
        for dcm_path in iterator:
            with transaction.atomic():
                image, created = self.get_or_create_from_dcm(dcm_path, autoremove=True)
            if report:
                counter_key = "created" if created else "existing"
                counter[counter_key] += 1
        if report:
            self.report_import_path_results(path, counter)
        return counter
