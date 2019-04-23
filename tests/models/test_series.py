from datetime import datetime
from django.test import TestCase
from django_dicom.models import Series, Patient, Study

TEST_SERIES_FIELDS = {
    "uid": "1.3.12.2.1107.5.2.43.66024.2017081508562441722500532.0.0.0",
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("08:56:36.246000", "%H:%M:%S.%f").time(),
    "description": "localizer_3D (9X5X5)",
    "number": 1,
    "echo_time": 3.04,
    "repetition_time": 7.6,
    "inversion_time": None,
    "scanning_sequence": ["GR"],
    "sequence_variant": ["SP", "OSP"],
    "pixel_spacing": [0.48828125, 0.48828125],
    "manufacturer": "SIEMENS",
    "manufacturer_model_name": "Prisma",
    "magnetic_field_strength": 3.0,
    "device_serial_number": "66024",
    "body_part_examined": "BRAIN",
    "patient_position": "HFS",
    "modality": "MR",
    "institution_name": "Tel-Aviv University",
    "protocol_name": "Ax1D_advdiff_d12D21_TE51_B1000",
    "flip_angle": 180.0,
    "mr_acquisition_type": "2D",
}
TEST_STUDY_FIELDS = {
    "uid": "1.3.12.2.1107.5.2.43.66024.30000018050107081466900000007",
    "description": "YA_lab^Assi",
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:21:56.958000", "%H:%M:%S.%f").time(),
}
TEST_PATIENT_FIELDS = {
    "uid": "304848286",
    "date_of_birth": datetime.strptime("19901214", "%Y%m%d").date(),
    "sex": "M",
    "given_name": "Zvi",
    "family_name": "Baratz",
}


class SeriesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(**TEST_PATIENT_FIELDS)
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        Series.objects.create(**TEST_SERIES_FIELDS)

    def setUp(self):
        self.series = Series.objects.get(uid=TEST_SERIES_FIELDS["uid"])

    def test_string(self):
        self.assertEqual(str(self.series), self.series.uid)

    def test_get_absolute_url(self):
        url = self.series.get_absolute_url()
        expected = f"/dicom/series/{self.series.id}/"
        self.assertEqual(url, expected)
