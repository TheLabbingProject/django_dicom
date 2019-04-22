# from django_dicom.data_import import ImportImage

# dir_path = os.path.dirname(os.path.realpath(__file__))
# TEST_IMAGE = os.path.join(dir_path, "../files/001.dcm")
# TEST_UID = "1.3.12.2.1107.5.2.43.66024.2018050112252318571884482"
# TEST_DATE = datetime.strptime("20180501", "%Y%m%d").date()
# TEST_TIME = datetime.strptime("12:25:23.268000", "%H:%M:%S.%f").time()


# class ImageTestCase(TestCase):
#     def setUp(self):
#         with open(TEST_IMAGE, "rb") as dcm:
#             self.image, self.created = ImportImage(dcm).run()

#     def test_image_created(self):
#         self.assertTrue(self.created)

#     def test_image_header_fields(self):
#         self.assertEqual(self.image.uid, TEST_UID)
#         self.assertEqual(self.image.number, 1)
#         self.assertEqual(self.image.date, TEST_DATE)
#         self.assertEqual(self.image.time, TEST_TIME)

#     def test_image_string(self):
#         self.assertEqual(str(self.image), self.image.uid)

#     def test_image_absolute_url(self):
#         namespace = "dicom"
#         pk = self.image.id
#         self.assertEqual(self.image.get_absolute_url(), f"/{namespace}/{pk}/")

#     def test_reading_file(self):
#         header = self.image.read_file(header_only=True)
#         self.assertIsInstance(header, pydicom.dataset.FileDataset)
#         with self.assertRaises(AttributeError):
#             header.pixel_array

#     def test_reading_file_data(self):
#         data = self.image.get_data()
#         self.assertIsInstance(data, np.ndarray)
#         self.assertEqual(data.shape, (512, 512))

#     def test_creating_header_instance(self):
#         header = self.image.read_header()
#         self.assertIsInstance(header, HeaderInformation)
