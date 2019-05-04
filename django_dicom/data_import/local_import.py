import os
import zipfile

from django_dicom.data_import.import_image import ImportImage
from django_dicom.models import Image
from tqdm import tqdm


class LocalImport:
    """
    This class handles importing data from a local directory. Any *.dcm* files 
    under the directory tree will be imported using :class:`~django_dicom.data_import.import_image.ImportImage`.

    TODO: This should be made into a custom django-admin command:
    https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/
    """

    def __init__(self, path: str):
        """
        Takes a path to be walked over for DICOM import.
        
        Parameters
        ----------
        path : str
            The base directory over the imported directory tree.
        
        """

        self.path = path

    @classmethod
    def import_local_dcm(cls, path: str) -> Image:
        """
        Reads the local DICOM image into an :class:`io.BufferedReader` and uses
        :class:`~django_dicom.data_import.import_image.ImportImage` to create an
        :class:`~django_dicom.models.Image` from it.
        
        Parameters
        ----------
        path : str
            The local path of the DICOM image.
        
        Returns
        -------
        Image
            The resulting :class:`~django_dicom.models.Image` instance.
        """

        with open(path, "rb") as dcm_buffer:
            return ImportImage(dcm_buffer).run()

    @classmethod
    def import_local_zip_archive(cls, path: str, verbose: bool = True) -> None:
        """
        Iterates over the files within a ZIP archive and imports any "*.dcm*" files.
        
        Parameters
        ----------
        path : str
            Local ZIP archive path.
        verbose : bool, optional
            Show a progressbar (default to True).
        """

        counter = {"created": 0, "existing": 0}
        zip_name = os.path.basename(path)
        if verbose:
            print(f"Reading {path}...")
        with zipfile.ZipFile(path, "r") as archive:
            for file_name in tqdm(archive.namelist(), disable=not verbose):
                if file_name.endswith(".dcm"):
                    with archive.open(file_name) as dcm_buffer:
                        _, created = ImportImage(dcm_buffer).run()
                        if created:
                            counter["created"] += 1
                        else:
                            counter["existing"] += 1
        msg = f"Successfully imported {counter['created']} new images from {zip_name}!"
        if counter["existing"]:
            msg += (
                f" ({counter['existing']} were found to already exist in the database)"
            )
        if verbose:
            print(msg)

    def path_generator(self, extension: str = "") -> str:
        """
        Generates paths from the given directory tree.

        Parameters
        ----------
        extension : str
            A file extension to filter the generated files with.

        Returns
        -------
        str
            File path.
        """

        for directory, _, files in os.walk(self.path):
            if extension:
                files = [f for f in files if f.endswith(f".{extension}")]
            for file_name in files:
                yield os.path.join(directory, file_name)

    def import_dcm_files(self, verbose: bool = True) -> None:
        """
        Creates :class:`~django_dicom.models.Image` instances for each "*.dcm*"
        file under the given directory tree. Prints an iterations counter and
        reports the number of instances added in the end.

        Parameters
        ----------
        verbose : bool, optional
            Shows an iterations/second meter (default to True).
        """

        counter = {"created": 0, "existing": 0}
        dcm_generator = self.path_generator(extension="dcm")
        if verbose:
            print("\nImporting DICOM image files...")
        for dcm_path in tqdm(dcm_generator, disable=not verbose):
            _, created = self.import_local_dcm(dcm_path)
            if created:
                counter["created"] += 1
            else:
                counter["existing"] += 1
        msg = f"Successfully imported {counter['created']} new images!"
        if counter["existing"]:
            msg += (
                f" ({counter['existing']} were found to already exist in the database)"
            )
        if verbose:
            print(msg)

    def import_zip_archives(self, verbose: bool = True) -> None:
        """
        Finds ZIP archives under the current directory tree and imports any DICOM
        data (*.dcm* files) found within them.

        Parameters
        ----------
        verbose : bool, optional
            Shows a progressbar (default to True).        
        """

        if verbose:
            print("\nChecking ZIP archives...")
        archives = self.path_generator(extension="zip")
        counter = 0
        for archive in archives:
            self.import_local_zip_archive(archive, verbose=verbose)
            counter += 1
        if verbose:
            if counter:
                noun = "archive"
                if counter > 1:
                    noun += "s"
                print(f"{counter} ZIP {noun} imported.")
            else:
                print("No ZIP archives found.")

    def run(self, import_zip: bool = True, verbose: bool = True) -> None:
        """
        Imports any DICOM data (*.dcm* files) found under the given path.
        
        Parameters
        ----------
        import_zip : bool, optional
            Find and import data from ZIP archives (the default is True, which will import any ZIP archived DICOM images).
        verbose : bool, optional
            Shows a progressbar (default to True).        
        """

        self.import_dcm_files(verbose=verbose)
        if import_zip:
            self.import_zip_archives(verbose=verbose)

