"""
Definition of the :class:`ImageManager` class.
"""
import logging
from io import BufferedReader
from pathlib import Path
from typing import Tuple

from dicom_parser.header import Header as DicomHeader
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import QuerySet
from pydicom.errors import InvalidDicomError

from django_dicom.models.managers.dicom_entity import DicomEntityManager
from django_dicom.models.managers.messages import IMPORT_ERROR, PATIENT_UID_MISMATCH
from django_dicom.models.utils.progressbar import create_progressbar

IMPORT_LOGGER = logging.getLogger("data_import")


class ImageManager(DicomEntityManager):
    """
    Custom :class:`~django.db.models.Manager` for the
    :class:`~django_dicom.models.image.Image` model.
    """

    #: Name given to DICOM files that need to be saved locally in order to be
    #: read.
    TEMP_DCM_FILE_NAME = "tmp.dcm"

    def store_image_data(self, image_data: BufferedReader) -> Path:
        """
        Stores binary image data to a temporary local path under the
        project's MEDIA_ROOT_.

        .. _MEDIA_ROOT:
           https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-MEDIA_ROOT

        Parameters
        ----------
        image_data : :class:`io.BufferedReader`
            Binary DICOM image data

        Returns
        -------
        :class:`pathlib.Path`
            Path of the created file
        """

        content = ContentFile(image_data.read())
        relative_path = default_storage.save(self.TEMP_DCM_FILE_NAME, content)
        return Path(settings.MEDIA_ROOT, relative_path)

    def create_from_dcm(self, path: Path, autoremove: bool = True):
        """
        Creates an :class:`~django_dicom.models.image.Image` instance from a
        given path.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Local *.dcm* file path
        autoremove : bool, optional
            Whether to remove the local copy of the *.dcm* file under
            MEDIA_ROOT if creation fails, by default True

        Returns
        -------
        :class:`~django_dicom.models.image.Image`
            The created image
        """

        try:
            return self.create(dcm=str(path))

        # In case the file is located outside MEDIA_ROOT (and therefore is
        # inaccessible), create an accessible copy and then initialize Image
        # instance.
        except SuspiciousFileOperation:
            with open(path, "rb") as data:
                local_path = self.store_image_data(data)
            return self.create_from_dcm(local_path, autoremove=autoremove)

        # If the creation failed, remove the local copy and re-raise the
        # exception.
        except Exception as e:
            if autoremove and path.is_file():
                path.unlink()
            message = IMPORT_ERROR.format(path=path, exception=e)
            raise RuntimeError(message)

    def get_or_create_from_dcm(self, path: Path, autoremove: bool = True) -> Tuple:
        """
        Gets or creates an :class:`~django_dicom.models.image.Image` instance
        based on the contents of the provided *.dcm* path.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Local *.dcm* file path
        autoremove : bool, optional
            Whether to remove the local copy of the *.dcm* file under
            MEDIA_ROOT if creation fails, by default True

        Returns
        -------
        Tuple[Image, bool]
            image, created
        """

        header = DicomHeader(path)
        uid = header.get("SOPInstanceUID")
        try:
            existing = self.get(uid=uid)
        except ObjectDoesNotExist:
            new_instance = self.create_from_dcm(path, autoremove=autoremove)
            return new_instance, True
        else:
            return existing, False

    def get_or_create(self, *args, **kwargs) -> Tuple:
        """
        Overrides
        :meth:`~django.db.models.manager.Manager.get_or_create` to call
        :meth:`~django_dicom.models.managers.image.ImageManager.get_or_create_from_dcm`
        in case the *dcm* keyword argument is provided.

        Returns
        -------
        Tuple[Image, bool]
            image, created
        """

        dcm_path = kwargs.get("dcm")
        if dcm_path:
            return self.get_or_create_from_dcm(Path(dcm_path))
        return super().get_or_create(*args, **kwargs)

    def report_import_path_results(self, path: Path, counter: dict) -> None:
        """
        Reports the result of a recursive path import.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Base path of DICOM data import
        counter : dict
            Dictionary containing *created* and *existing* keys containing the
            number of files which fit in each category.
        """

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
        self,
        path: Path,
        progressbar: bool = True,
        report: bool = True,
        persistent: bool = True,
        pattern: bool = "*.dcm",
        autoremove: bool = True,
    ) -> QuerySet:
        """
        Iterates the given directory tree and imports any *.dcm* files found
        within it.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Base path for recursive *.dcm* import
        progressbar : bool, optional
            Whether to display a progressbar or not, by default True
        report : bool, optional
            Whether to print out a summary report when finished or not, by
            default True
        persistent : bool, optional
            Whether to continue and raise a warning or to raise an exception
            when failing to read a DICOM file's header
        pattern : str, optional
            Globbing pattern to use for file import

        Returns
        -------
        :class:`~django.db.models.query.QuerySet`
            The created :class:`~django_dicom.models.image.Image` instances
        """

        # Create an iterator
        iterator = Path(path).rglob(pattern)
        if progressbar:
            # Create a progressbar wrapped iterator using tqdm
            iterator = create_progressbar(iterator, unit="image")

        if report:
            counter = {"created": 0, "existing": 0}

        # Keep a list of all the created images' primary keys
        created_ids = []

        # Keep a list of patient UID mismatches to log
        patient_uid_mismatch = []

        for dcm_path in iterator:

            if not dcm_path.is_file():
                continue

            # Atomic image import
            # For more information see:
            # https://docs.djangoproject.com/en/3.0/topics/db/transactions/#controlling-transactions-explicitly
            with transaction.atomic():
                try:
                    image, created = self.get_or_create_from_dcm(
                        dcm_path, autoremove=autoremove
                    )
                except InvalidDicomError as e:
                    if not persistent:
                        raise

                    IMPORT_LOGGER.warning(e)
                    continue
            if report:
                counter_key = "created" if created else "existing"
                counter[counter_key] += 1

            if created:
                created_ids.append(image.id)
            elif image.patient.uid not in patient_uid_mismatch:
                # Validate patient UID for existing images
                header = DicomHeader(dcm_path)
                patient_uid = header.get("PatientID")
                if patient_uid != image.patient.uid:
                    # Log patient UID mismatch
                    image_uid = header.get("SOPInstanceUID")
                    message = PATIENT_UID_MISMATCH.format(
                        image_uid=image_uid,
                        db_value=image.patient.uid,
                        patient_uid=patient_uid,
                    )
                    IMPORT_LOGGER.warning(message)
                    patient_uid_mismatch.append(image.patient.uid)
        if report:
            self.report_import_path_results(path, counter)

        return self.filter(id__in=created_ids)
