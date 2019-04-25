import glob
import os
import shutil

from django.conf import settings
from django.test import TestCase
from django_dicom.apps import DjangoDicomConfig
from django_dicom.data_import.import_image import ImportImage
from django_dicom.models import Image, Series, Study, Patient
from tests.fixtures import (
    TEST_IMAGE_PATH,
    TEST_DWI_IMAGE_PATH,
    TEST_DIFFERENT_STUDY_IMAGE_PATH,
    TEST_DIFFERENT_PATIENT_IMAGE_PATH,
    TEST_SERIES_FIELDS,
    TEST_DWI_SERIES_FIELDS,
    TEST_PATIENT_FIELDS,
    TEST_STUDY_FIELDS,
)

TESTS_DIR = os.path.normpath("./tests")
TEMP_FILES = os.path.join(TESTS_DIR, "tmp*.dcm")
IMPORTED_DIR = os.path.join(TESTS_DIR, "MRI")


class ImportImageTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.data_import.import_image.ImportImage` class
    which is meant to handle the addition of new DICOM images to the database.

    """

    @classmethod
    def setUpTestData(cls):
        """
        Creates :class:`~django_dicom.models.series.Series`, :class:`~django_dicom.models.study.Study`,
        and :class:`~django_dicom.models.patient.Patient` instances to test for cases
        in which we add DICOM images under these conditions (related entities exist).
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        
        """

        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(**TEST_PATIENT_FIELDS)
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        Series.objects.create(**TEST_SERIES_FIELDS)

    def tearDown(self):
        """
        Delete any temporary files that may have been created during the
        :class:`~django_dicom.models.image.Image` instance's creation.
        For more information see unittest's :meth:`~unittest.TestCase.tearDown` method.

        """

        for dcm in glob.glob(TEMP_FILES):
            os.remove(dcm)

    def test_store_file(self):
        # Store file
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            temporary_name = instance.store_file()
        # Test that the returned path is valid and has the dcm extension
        temporary_path = os.path.join(settings.MEDIA_ROOT, temporary_name)
        is_file = os.path.isfile(temporary_path)
        has_correct_extension = temporary_name.endswith(
            DjangoDicomConfig.data_extension
        )
        self.assertTrue(is_file)
        self.assertTrue(has_correct_extension)

    def test_create_image(self):
        # Create image
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            image = instance.create_image()
        # Test return type
        self.assertIsInstance(image, Image)
        # Test that the Image instance was initialized with a valid path
        image_points_to_real_file = os.path.isfile(image.dcm.path)
        self.assertTrue(image_points_to_real_file)

    def test_get_entity_uid_from_header(self):
        # Create image
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            instance.image = instance.create_image()
        # Get the expected values
        series_uid = instance.image.header.get_value("SeriesInstanceUID")
        study_uid = instance.image.header.get_value("StudyInstanceUID")
        patient_uid = instance.image.header.get_value("PatientID")
        # Get the returned values
        series_result = instance.get_entity_uid_from_header(Series)
        study_result = instance.get_entity_uid_from_header(Study)
        patient_result = instance.get_entity_uid_from_header(Patient)
        # Test equality
        self.assertEqual(series_result, series_uid)
        self.assertEqual(study_result, study_uid)
        self.assertEqual(patient_result, patient_uid)

    def test_get_or_create_entity_with_existing_entities(self):
        # Create image
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            instance.image = instance.create_image()
        # Tests entities are returned and are not created
        for Entity in (Series, Study, Patient):
            entity, created = instance.get_or_create_entity(Entity)
            self.assertFalse(created)
            self.assertIsInstance(entity, Entity)

    def test_get_or_create_entity_with_missing_entities(self):
        # Create image
        with open(TEST_DIFFERENT_PATIENT_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            instance.image = instance.create_image()
        # Test entities are returned and are not created
        for Entity in (Series, Study, Patient):
            # We are not saving to the database in order to avoid the required
            # relationships between the entites, as they are not managed here.
            entity, created = instance.get_or_create_entity(Entity, save=False)
            self.assertTrue(created)
            self.assertIsInstance(entity, Entity)
            # Make sure the created entity has updated fields
            self.assertIsNotNone(entity.uid)

    def test_get_image_destination(self):
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            instance.image = instance.create_image()
        # The get_image_destination method used the Image instance number field
        # in order to create the file name.
        instance.image.number = 1
        destination = instance.get_image_destination()
        expected = "MRI/304848286/1.3.12.2.1107.5.2.43.66024.2018050112250992296484473.0.0.0/DICOM/1.dcm"
        self.assertEqual(destination, expected)

    def test_move_image_to_destination(self):
        # Create an image with updated fields
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            instance.image = instance.create_image()
            instance.image.update_fields_from_header(instance.image.header)
        # Test that the returned relative path is a valid path under MEDIA_ROOT
        relative_destination = instance.move_image_to_destination()
        destination = os.path.join(settings.MEDIA_ROOT, relative_destination)
        self.assertTrue(os.path.isfile(destination))
        shutil.rmtree(IMPORTED_DIR)

    def test_generate_entities_and_relationships(self):
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            instance = ImportImage(dcm)
            instance.generate_entities_and_relationships()
        self.assertIsInstance(instance.image, Image)
        self.assertIsInstance(instance.image.series, Series)
        self.assertIsInstance(instance.image.series.study, Study)
        self.assertIsInstance(instance.image.series.patient, Patient)

    def test_run_with_existing_related_entities(self):
        # Create image
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            image, created = ImportImage(dcm).run()
        self.assertIsInstance(image, Image)
        self.assertTrue(created)
        # Get the expected values
        series = Series.objects.get(uid=TEST_SERIES_FIELDS["uid"])
        study = Study.objects.get(uid=TEST_STUDY_FIELDS["uid"])
        patient = Patient.objects.get(uid=TEST_PATIENT_FIELDS["uid"])
        # Test equality
        self.assertEqual(image.series, series)
        self.assertEqual(image.series.study, study)
        self.assertEqual(image.series.patient, patient)
        shutil.rmtree(IMPORTED_DIR)

    def test_run_with_different_series_but_same_patient_and_study(self):
        # Create image
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            image, _ = ImportImage(dcm).run()
        # Create image from same patient and study but different series
        with open(TEST_DWI_IMAGE_PATH, "rb") as dcm:
            dwi, created = ImportImage(dcm).run()
        self.assertIsInstance(dwi, Image)
        self.assertTrue(created)
        # Test new series and existing patient and study were related
        self.assertEqual(dwi.series.uid, TEST_DWI_SERIES_FIELDS["uid"])
        self.assertNotEqual(dwi.series, image.series)
        self.assertEqual(dwi.series.study, image.series.study)
        self.assertEqual(dwi.series.patient, image.series.patient)
        shutil.rmtree(IMPORTED_DIR)

    def test_run_with_different_study_and_same_patient(self):
        # Create image
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            image, _ = ImportImage(dcm).run()
        # Create image from same patient and study but different series
        with open(TEST_DIFFERENT_STUDY_IMAGE_PATH, "rb") as dcm:
            later_image, created = ImportImage(dcm).run()
        self.assertIsInstance(later_image, Image)
        self.assertTrue(created)
        # Test new series and study but existing patientwere related
        self.assertNotEqual(later_image.series, image.series)
        self.assertNotEqual(later_image.series.study, image.series.study)
        self.assertEqual(later_image.series.patient, image.series.patient)
        shutil.rmtree(IMPORTED_DIR)

    def test_run_with_different_patient_and_same_study(self):
        # TODO: Find two images from same study and different patient and complete this.
        # Create images
        # Test new series and study but existing patientwere related
        # self.assertNotEqual(second_image.series, image.series)
        # self.assertEqual(second_image.series.study, image.series.study)
        # self.assertNotEqual(
        #     second_image.series.patient, image.series.patient
        # )
        pass

    def test_run_with_different_patient_and_different_study(self):
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            image, _ = ImportImage(dcm).run()
        with open(TEST_DIFFERENT_PATIENT_IMAGE_PATH, "rb") as dcm:
            second_image, _ = ImportImage(dcm).run()
        self.assertNotEqual(image, second_image)
        self.assertNotEqual(image.series, second_image.series)
        self.assertNotEqual(image.series.study, second_image.series.study)
        self.assertNotEqual(image.series.patient, second_image.series.patient)
        shutil.rmtree(IMPORTED_DIR)

    def test_run_with_integrity_error_handler(self):
        # Normal run
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            image, created = ImportImage(dcm).run()
        self.assertIsInstance(image, Image)
        self.assertTrue(created)
        # Adding the same instance should invoke the handle_integrity_error method
        with open(TEST_IMAGE_PATH, "rb") as dcm:
            same_image, created_again = ImportImage(dcm).run()
        self.assertEqual(image, same_image)
        self.assertFalse(created_again)
        shutil.rmtree(IMPORTED_DIR)

    def test_run_with_different_integrity_error(self):
        # Not sure how to go about this.
        pass
