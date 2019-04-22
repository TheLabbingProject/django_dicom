# import numpy as np
import os

# import pydicom

from datetime import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dicom.apps import DjangoDicomConfig
from django_dicom.models import Image, Series

# from django_dicom.reader import HeaderInformation


dir_path = os.path.dirname(os.path.realpath(__file__))
TEST_IMAGE_PATH = os.path.join(dir_path, "../files/001.dcm")
TEST_IMAGE_FIELDS = {
    "dcm": TEST_IMAGE_PATH,
    "uid": "1.3.12.2.1107.5.2.43.66024.2018050112252318571884482",
    "number": 1,
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:25:23.268000", "%H:%M:%S.%f").time(),
}
TEST_SERIES_FIELDS = {
    "uid": "1.3.12.2.1107.5.2.43.66024.2017081508562441722500532.0.0.0",
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("08:56:36.246000", "%H:%M:%S.%f").time(),
    "description": "localizer_3D (9X5X5)",
    "number": 1,
}


class ImageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        TEST_IMAGE_FIELDS["series"] = Series.objects.create(**TEST_SERIES_FIELDS)
        Image.objects.create(**TEST_IMAGE_FIELDS)

    def setUp(self):
        self.image = Image.objects.get(id=1)

    def test_dcm_extension_validation(self):
        """
        Tests that only *.dcm* files may be used to instantiate an
        :class:`~django_dicom.models.image.Image` instance.
        
        """

        file_name = self.image.dcm.name
        extension = DjangoDicomConfig.data_extension
        self.image.dcm.name = file_name.replace(extension, ".abc")
        with self.assertRaises(ValidationError):
            self.image.full_clean()

    def test_image_uid_max_length(self):
        """
        DICOM's SOPInstanceUID_ attribute may only be as long as 64 characters (
        see the UI `value-representation specification`).

        .. _SOPInstanceUID: https://dicom.innolitics.com/ciods/mr-image/sop-common/00080018
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.image._meta.get_field("uid")
        self.assertEqual(field.max_length, 64)

    def test_image_uid_validation(self):
        """
        An :class:`~django_dicom.models.image.Image` instance UID field may only
        be composed of dots and digits.
        
        """

        non_digit_or_dot_chars = [
            "+",
            "=",
            ")",
            "(",
            "*",
            "&",
            "^",
            "%",
            "$",
            "#",
            "@",
            "!",
        ]
        uid = self.image.uid
        for character in non_digit_or_dot_chars:
            self.image.uid = character + uid[1:]
            with self.assertRaises(ValidationError):
                self.image.full_clean()
        self.image.uid = uid

    def test_image_uid_vebose_name(self):
        """
        Test the UID field vebose name.
        
        """

        field = self.image._meta.get_field("uid")
        self.assertEqual(field.verbose_name, "Image UID")

    def test_image_number_vebose_name(self):
        """
        Test the *number* field vebose name.
        
        """

        field = self.image._meta.get_field("number")
        self.assertEqual(field.verbose_name, "Image Number")

    def test_fields_blank_and_null_configuration(self):
        """
        Every :class:`~django_dicom.models.image.Image` instance must have all of
        their fields set. *id*, *created*, and *modified* my be blank in forms.
        
        """

        for field in self.image._meta.get_fields():
            if field.name in ["id", "created", "modified"]:
                self.assertTrue(field.blank, f"{field.name} should be blankable!")
            else:
                self.assertFalse(field.blank, f"{field.name} should not be blankable!")
            self.assertFalse(field.null, f"{field.name} should not be nullable!")

    def test_image_string(self):
        self.assertEqual(str(self.image), self.image.uid)
