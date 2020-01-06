import os
import shutil

from django.test import TestCase
from django_dicom.data_import.local_import import LocalImport
from django_dicom.models.image import Image
from tests.fixtures import TEST_FILES_PATH, TEST_IMAGE_PATH, TEST_ZIP_PATH


TESTS_DIR = os.path.normpath("./tests")
TEMP_FILES = os.path.join(TESTS_DIR, "tmp*.dcm")
IMPORTED_DIR = os.path.join(TESTS_DIR, "MRI")


class LocalImportTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.data_import.local_import.LocalImport` class,
    which is meant to provide methods to facilitate data import.
    
    """

    def tearDown(self):
        """
        Tries to remove the :class:`~django_dicom.models.image.Image` instances
        that may have been created during each test, as well as the destination
        directory.
        For more information see unittest's :meth:`~unittest.TestCase.tearDown` method.

        """

        Image.objects.all().delete()
        try:
            shutil.rmtree(IMPORTED_DIR)
        except FileNotFoundError:
            pass

    def test_initialization(self):
        """
        Tests that the :class:`~django_dicom.data_import.local_import.LocalImport`
        class is initialized properly.

        """

        instance = LocalImport(TEST_IMAGE_PATH)
        self.assertEqual(instance.path, TEST_IMAGE_PATH)

    def test_import_local_dcm(self):
        """
        Tests importing a single DICOM image from some path using
        :meth:`~django_dicom.data_import.local_import.LocalImport.import_local_dcm`.
        
        """

        image, created = LocalImport.import_local_dcm(TEST_IMAGE_PATH)
        self.assertTrue(created)
        self.assertIsInstance(image, Image)

        # Also check that the created instance is updated
        self.assertIsNotNone(image.uid)
        self.assertIsNotNone(image.series)
        self.assertIsNotNone(image.series.study)
        self.assertIsNotNone(image.series.patient)

    def test_import_local_zip_archive(self):
        """
        Tests importing DICOM images from a single ZIP archive using
        :meth:`~django_dicom.data_import.local_import.LocalImport.import_local_zip_archive`.
        
        """

        self.assertEqual(Image.objects.count(), 0)
        LocalImport.import_local_zip_archive(TEST_ZIP_PATH, verbose=False)
        # The ZIP archive contains 3 images
        self.assertEqual(Image.objects.count(), 3)

    def test_path_generator_without_extension(self):
        """
        Tests the :meth:`~django_dicom.data_import.local_import.LocalImport.path_generator`
        method with no *extension* parameter setting.
        
        """

        counter = 0
        for path in LocalImport(TEST_FILES_PATH).path_generator():
            is_valid_path = os.path.isfile(path)
            self.assertTrue(is_valid_path)
            is_under_base_dir = path.startswith(TEST_FILES_PATH)
            self.assertTrue(is_under_base_dir)
            counter += 1
        # There are 6 files in the given path
        self.assertEqual(counter, 6)

    def test_path_generator_with_extension(self):
        """
        Tests the :meth:`~django_dicom.data_import.local_import.LocalImport.path_generator`
        method with the *extension* parameter set.
        
        """

        # A dictionary of extensions and the number of files we expect
        extensions = {"zip": 2, "dcm": 4}

        for extension in extensions:
            counter = 0
            generator = LocalImport(TEST_FILES_PATH).path_generator(extension=extension)
            for path in generator:
                is_valid_path = os.path.isfile(path)
                self.assertTrue(is_valid_path)
                is_under_base_dir = path.startswith(TEST_FILES_PATH)
                self.assertTrue(is_under_base_dir)
                counter += 1
            self.assertEqual(counter, extensions.get(extension))

    def test_import_dcm_files(self):
        """
        Tests importing multiple DICOM images at once using the
        :meth:`~django_dicom.data_import.local_import.LocalImport.import_dcm_files`
        method.

        """

        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).import_dcm_files(verbose=False)
        # There are 4 DICOM images in the test files directory.
        self.assertEqual(Image.objects.count(), 4)

    def test_import_zip_archives(self):
        """
        Tests importing DICOM images from multiple ZIP archives at once using the
        :meth:`~django_dicom.data_import.local_import.LocalImport.import_zip_archives`
        method.

        """

        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).import_zip_archives(verbose=False)
        # The ZIP archives contain a total of 4 (unique) DICOM images.
        self.assertEqual(Image.objects.count(), 4)

    def test_run_with_zip_archives(self):
        """
        Tests the :class:`~django_dicom.data_import.local_import.LocalImport` class's        
        :meth:`~django_dicom.data_import.local_import.LocalImport.run` method when
        set to include ZIP archives.

        """

        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).run(import_zip=True, verbose=False)
        # The test files directory contains a total of 8 (unique) DICOM images.
        self.assertEqual(Image.objects.count(), 8)

    def test_run_without_zip_archives(self):
        """
        Tests the :class:`~django_dicom.data_import.local_import.LocalImport` class's        
        :meth:`~django_dicom.data_import.local_import.LocalImport.run` method when
        set to exclude ZIP archives.

        """

        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).run(import_zip=False, verbose=False)
        # There are 4 DICOM images in the test files directory.
        self.assertEqual(Image.objects.count(), 4)

    def test_run_default_configuration(self):
        """
        Tests the :class:`~django_dicom.data_import.local_import.LocalImport` class's        
        :meth:`~django_dicom.data_import.local_import.LocalImport.run` method's
        default configuration is to include ZIP archives.
        
        """

        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).run(verbose=False)
        # The test files directory contains a total of 8 (unique) DICOM images.
        self.assertEqual(Image.objects.count(), 8)
