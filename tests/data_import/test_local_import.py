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
    def tearDown(self):
        Image.objects.all().delete()
        try:
            shutil.rmtree(IMPORTED_DIR)
        except FileNotFoundError:
            pass

    def test_init(self):
        instance = LocalImport(TEST_IMAGE_PATH)
        self.assertEqual(instance.path, TEST_IMAGE_PATH)

    def test_import_local_dcm(self):
        image, created = LocalImport.import_local_dcm(TEST_IMAGE_PATH)
        self.assertTrue(created)
        self.assertIsInstance(image, Image)
        self.assertIsNotNone(image.uid)
        self.assertIsNotNone(image.series)
        self.assertIsNotNone(image.series.study)
        self.assertIsNotNone(image.series.patient)

    def test_import_local_zip_archive(self):
        self.assertEqual(Image.objects.count(), 0)
        LocalImport.import_local_zip_archive(TEST_ZIP_PATH, verbose=False)
        self.assertEqual(Image.objects.count(), 3)

    def test_path_generator_without_extension(self):
        counter = 0
        for path in LocalImport(TEST_FILES_PATH).path_generator():
            is_valid_path = os.path.isfile(path)
            self.assertTrue(is_valid_path)
            is_under_base_dir = path.startswith(TEST_FILES_PATH)
            self.assertTrue(is_under_base_dir)
            counter += 1
        self.assertEqual(counter, 6)

    def test_path_generator_with_extension(self):
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
        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).import_dcm_files(verbose=False)
        self.assertEqual(Image.objects.count(), 4)

    def test_import_zip_archives(self):
        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).import_zip_archives(verbose=False)
        self.assertEqual(Image.objects.count(), 4)

    def test_run_with_zip_archives(self):
        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).run(import_zip=True, verbose=False)
        self.assertEqual(Image.objects.count(), 8)

    def test_run_without_zip_archives(self):
        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).run(import_zip=False, verbose=False)
        self.assertEqual(Image.objects.count(), 4)

    def test_run_default_configuration(self):
        self.assertEqual(Image.objects.count(), 0)
        LocalImport(TEST_FILES_PATH).run(verbose=False)
        self.assertEqual(Image.objects.count(), 8)
