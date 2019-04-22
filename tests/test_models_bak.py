# import numpy as np
# import os
# import pydicom

# from datetime import date, time
# from django_dicom.models import Image
# from django_dicom.tests.factories import (
#     ImageFactory,
#     get_test_file_path,
#     TEST_FILES_PATH,
#     SERIES_FILES,
# )
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.test import TestCase


# class ImageModelTestCase(TestCase):
#     TEST_IMAGES = [
#         "test",
#         "same_series",
#         "different_series",
#         "different_study_same_patient",
#         # 'different_patient_same_study',
#         "different_patient_different_study",
#     ]

#     TEST_IMAGE_UIDS = [
#         "1.3.12.2.1107.5.2.43.66024.2016120813110917216691062",
#         "1.3.12.2.1107.5.2.43.66024.2016120813113249580291102",
#         "1.3.12.2.1107.5.2.43.66024.2016120813140464245591454",
#         "1.3.12.2.1107.5.2.43.66024.2018050112252318571884482",
#         "1.3.12.2.1107.5.2.43.66024.2016121412223453546567775",
#     ]

#     ZIPPED_UIDS = [
#         "1.3.12.2.1107.5.2.43.66024.2016120813301385447497555",
#         "1.3.12.2.1107.5.2.43.66024.2016120813360043323300309",
#         "1.3.12.2.1107.5.2.43.66024.2016120813262299647895751",
#         "1.3.12.2.1107.5.2.43.66024.2016121412432166520775187",
#         "1.3.12.2.1107.5.2.43.66024.201612141317482895906735",
#         "1.3.12.2.1107.5.2.43.66024.2016121412485542898477604",
#     ]

#     def setUp(self):
#         self.create_all_test_images()

#     def load_uploaded_dcm(self):
#         with open(get_test_file_path("from_file"), "rb") as test_file:
#             return SimpleUploadedFile(test_file.name, test_file.read())

#     def load_uploaded_zip(self):
#         relative_path = os.path.join(TEST_FILES_PATH, "test.zip")
#         source = os.path.abspath(relative_path)
#         with open(source, "rb") as test_zip:
#             return SimpleUploadedFile(test_zip.name, test_zip.read())

#     def create_all_test_images(self):
#         for name in self.TEST_IMAGES:
#             path = get_test_file_path(name)
#             image = ImageFactory(file__from_path=path)
#             image.save()

#     def get_image(self, name: str) -> Image:
#         index = self.TEST_IMAGES.index(name)
#         return Image.objects.get(uid=self.TEST_IMAGE_UIDS[index])

#     def test_str(self):
#         self.assertEqual(str(self.test_image), self.test_image.header.SOPImageUID)

#     def test_get_image_data(self):
#         data = self.test_image.read_data()
#         self.assertIsImage(data, pydicom.dataset.FileDataset)
#         self.assertTrue(hasattr(data, "pixel_array"))

#     def test_get_image_header(self):
#         data = self.test_image.read_header()
#         self.assertIsImage(data, pydicom.dataset.FileDataset)
#         with self.assertRaises(TypeError):
#             data.pixel_array

#     def test_image_uid(self):
#         self.assertEqual(self.test_image.image_uid, self.test_image.header.SOPImageUID)

#     def test_image_number(self):
#         self.assertEqual(self.test_image.number, self.test_image.header.ImageNumber)

#     def test_image_date(self):
#         self.assertEqual(self.test_image.date, date(2016, 12, 8))

#     def test_image_time(self):
#         self.assertEqual(self.test_image.time, time(13, 11, 9, 254_000))

#     def test_series_creation(self):
#         self.assertIsNotNone(self.test_image.series)

#     def test_series_uid(self):
#         new_series_uid = self.test_image.series.series_uid
#         expected_uid = self.test_image.header.SeriesImageUID
#         self.assertEqual(new_series_uid, expected_uid)

#     def test_series_number(self):
#         self.assertEqual(
#             self.test_image.series.number, self.test_image.header.SeriesNumber
#         )

#     def test_series_date(self):
#         self.assertEqual(self.test_image.series.date, date(2016, 12, 8))

#     def test_series_time(self):
#         self.assertEqual(self.test_image.series.time, time(13, 11, 9, 251_000))

#     def test_series_description(self):
#         self.assertEqual(
#             self.test_image.series.description, self.test_image.header.SeriesDescription
#         )

#     def test_study_creation(self):
#         self.assertIsNotNone(self.test_image.study)

#     def test_series_study_is_image_study(self):
#         self.assertEqual(self.test_image.study, self.test_image.series.study)

#     def test_study_date(self):
#         self.assertEqual(self.test_image.study.date, date(2016, 12, 8))

#     def test_study_time(self):
#         self.assertEqual(self.test_image.study.time, time(13, 5, 56, 90000))

#     def test_study_description(self):
#         self.assertEqual(
#             self.test_image.study.description, self.test_image.header.StudyDescription
#         )

#     def test_patient_creation(self):
#         self.assertIsNotNone(self.test_image.patient)

#     def test_series_patient_is_image_patient(self):
#         self.assertEqual(self.test_image.patient, self.test_image.series.patient)

#     def test_patient_id(self):
#         self.assertEqual(
#             self.test_image.patient.patient_id, self.test_image.header.PatientID
#         )

#     def test_patient_given_name(self):
#         self.assertEqual(
#             self.test_image.patient.given_name,
#             self.test_image.header.PatientName.given_name,
#         )

#     def test_patient_family_name(self):
#         self.assertEqual(
#             self.test_image.patient.family_name,
#             self.test_image.header.PatientName.family_name,
#         )

#     def test_patient_middle_name(self):
#         self.assertEqual(
#             self.test_image.patient.middle_name,
#             self.test_image.header.PatientName.middle_name,
#         )

#     def test_patient_name_prefix(self):
#         self.assertEqual(
#             self.test_image.patient.name_prefix,
#             self.test_image.header.PatientName.name_prefix,
#         )

#     def test_patient_name_suffix(self):
#         self.assertEqual(
#             self.test_image.patient.name_suffix,
#             self.test_image.header.PatientName.name_suffix,
#         )

#     def test_patient_birthdate(self):
#         self.assertIsImage(self.test_image.patient.date_of_birth, date)

#     def test_file_moved_to_default_location(self):
#         default_location = self.test_image.get_default_file_name()
#         self.assertTrue(self.test_image.file.path.endswith(default_location))

#     def test_same_series_image_has_same_series(self):
#         self.assertEqual(self.test_image.series, self.same_series_image.series)

#     def test_same_series_image_has_same_patient(self):
#         self.assertEqual(self.test_image.patient, self.same_series_image.patient)

#     def test_same_series_image_has_same_study(self):
#         self.assertEqual(self.test_image.study, self.same_series_image.study)

#     def test_different_series_image_has_different_series(self):
#         self.assertNotEqual(self.test_image.series, self.different_series_image.series)

#     def test_different_series_image_has_same_patient(self):
#         self.assertEqual(self.test_image.patient, self.different_series_image.patient)

#     def test_different_series_image_has_same_study(self):
#         self.assertEqual(self.test_image.study, self.different_series_image.study)

#     def test_different_study_same_patient_image_has_different_study(self):
#         self.assertNotEqual(
#             self.test_image.study, self.different_study_same_patient_image.study
#         )

#     def test_different_study_same_patient_image_has_same_patient(self):
#         self.assertEqual(
#             self.test_image.patient, self.different_study_same_patient_image.patient
#         )

#     def test_different_patient_different_study_image_has_different_patient(self):
#         self.assertNotEqual(
#             self.test_image.patient,
#             self.different_patient_different_study_image.patient,
#         )

#     def test_different_patient_different_study_image_has_different_study(self):
#         self.assertNotEqual(
#             self.test_image.study, self.different_patient_different_study_image.study
#         )

#     def test_image_creation_from_uploaded_dcm(self):
#         uploaded_dcm = self.load_uploaded_dcm()
#         image = Image.objects.from_dcm(uploaded_dcm)
#         self.assertIsImage(image, Image)
#         self.assertIsNotNone(image.image_uid)

#     def test_images_creation_from_uploaded_zip(self):
#         uploaded_zip = self.load_uploaded_zip()
#         Image.objects.from_zip(uploaded_zip)
#         for uid in self.ZIPPED_UIDS:
#             self.assertIsNotNone(Image.objects.get(image_uid=uid))

#     @property
#     def test_image(self):
#         return self.get_image("test")

#     @property
#     def same_series_image(self):
#         return self.get_image("same_series")

#     @property
#     def different_series_image(self):
#         return self.get_image("different_series")

#     @property
#     def different_study_same_patient_image(self):
#         return self.get_image("different_study_same_patient")

#     # TODO: Add different patient same study test

#     @property
#     def different_patient_different_study_image(self):
#         return self.get_image("different_patient_different_study")


# class StudyModelTestCase(TestCase):
#     def setUp(self):
#         path = get_test_file_path("test")
#         test_image = ImageFactory(file__from_path=path)
#         test_image.save()
#         self.test_study = test_image.study

#     def test_str(self):
#         self.assertEqual(str(self.test_study), self.test_study.study_uid)


# class SeriesModelTestCase(TestCase):
#     def setUp(self):
#         for path in SERIES_FILES:
#             image = ImageFactory(file__from_path=path)
#             image.save()
#         self.test_series = image.series

#     def test_str(self):
#         self.assertEqual(str(self.test_series), self.test_series.series_uid)

#     def test_verbose_name(self):
#         self.assertEqual(self.test_series._meta.verbose_name_plural, "Series")

#     def test_getting_data(self):
#         data = self.test_series.get_data()
#         self.assertIsImage(data, np.ndarray)
#         self.assertEqual(data.shape, (512, 512, 19))


# class PatientModelTestCase(TestCase):
#     def setUp(self):
#         path = get_test_file_path("test")
#         test_image = ImageFactory(file__from_path=path)
#         test_image.save()
#         self.test_patient = test_image.patient

#     def test_str(self):
#         self.assertEqual(str(self.test_patient), self.test_patient.patient_id)

#     def test_getting_patient_attributes(self):
#         expected = {
#             "first_name": self.test_patient.given_name,
#             "last_name": self.test_patient.family_name,
#             "date_of_birth": self.test_patient.date_of_birth,
#             "sex": self.test_patient.sex,
#             "id_number": self.test_patient.patient_id,
#         }
#         self.assertEqual(self.test_patient.get_patient_attributes(), expected)
