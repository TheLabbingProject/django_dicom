import numpy as np
import pydicom

from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dicom.apps import DjangoDicomConfig
from django_dicom.models import Image, Series, Patient, Study
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.reader import HeaderInformation
from django_dicom.utils import snake_case_to_camel_case
from tests.fixtures import (
    # TEST_IMAGE_PATH,
    # TEST_DWI_IMAGE_PATH,
    TEST_IMAGE_FIELDS,
    TEST_DWI_IMAGE_FIELDS,
    TEST_SERIES_FIELDS,
    TEST_DWI_SERIES_FIELDS,
    TEST_STUDY_FIELDS,
    TEST_PATIENT_FIELDS,
)


class ImageTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.image.Image` model.    

    """

    NON_HEADER_FIELDS = ["id", "dcm", "created", "modified", "series"]
    HEADER_FIELDS = ["uid", "number", "date", "time"]

    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to test the :class:`~django_dicom.models.image.Image`
        model.
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        """

        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(**TEST_PATIENT_FIELDS)
        TEST_DWI_SERIES_FIELDS["patient"] = TEST_SERIES_FIELDS["patient"]
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        TEST_DWI_SERIES_FIELDS["study"] = TEST_SERIES_FIELDS["study"]
        TEST_IMAGE_FIELDS["series"] = Series.objects.create(**TEST_SERIES_FIELDS)
        TEST_DWI_IMAGE_FIELDS["series"] = Series.objects.create(
            **TEST_DWI_SERIES_FIELDS
        )
        Image.objects.create(**TEST_IMAGE_FIELDS)
        Image.objects.create(**TEST_DWI_IMAGE_FIELDS)

    def setUp(self):
        """
        Adds the created instances to the tests' contexts.
        For more information see unittest's :meth:`~unittest.TestCase.setUp` method.

        """

        self.series = Series.objects.get(uid=TEST_SERIES_FIELDS["uid"])
        self.image = Image.objects.get(uid=TEST_IMAGE_FIELDS["uid"])
        self.dwi_series = Series.objects.get(uid=TEST_DWI_SERIES_FIELDS["uid"])
        self.dwi_image = Image.objects.get(uid=TEST_DWI_IMAGE_FIELDS["uid"])

    #######################################
    # Tests for DicomEntity functionality #
    #######################################

    def test_is_dicom_entity(self):
        """
        Tests that the created :class:`~django_dicom.models.image.Image` instance
        inherits from :class:`~django_dicom.models.dicom_entity.DicomEntity`.

        """

        self.assertIsInstance(self.image, DicomEntity)

    def test_get_header_keyword(self):
        """
        Tests that the :meth:`~django_dicom.models.dicom_entity.DicomEntity.get_header_keyword`
        method returns the keyword defined in the :class:`~django_dicom.models.image.Image`
        class's FIELD_TO_HEADER dictionary, or a CamelCase version of the field
        name if no such definition exists.

        """

        for field in self.image._meta.get_fields():
            if field.name in self.image.FIELD_TO_HEADER:
                expected = self.image.FIELD_TO_HEADER[field.name]
                result = self.image.get_header_keyword(field.name)
                self.assertEqual(result, expected)
            else:
                expected = snake_case_to_camel_case(field.name)
                result = self.image.get_header_keyword(field.name)
                self.assertEqual(result, expected)

    def test_is_header_field(self):
        """
        Tests that the :meth:`~django_dicom.models.dicom_entity.DicomEntity.is_header_field`
        method returns the correct boolean result for the different fields. Relies on this
        TestCase's defintion for the NON_HEADER_FIELDS class attribute.

        """

        for field in self.image._meta.get_fields():
            if field.name in self.NON_HEADER_FIELDS:
                self.assertFalse(self.image.is_header_field(field))
            else:
                self.assertTrue(self.image.is_header_field(field))

    def test_get_header_fields(self):
        """
        Tests that the :meth:`~django_dicom.models.dicom_entity.DicomEntity.get_header_fields`
        returns the correct fields. The expected fields should be set as this TestCase's
        HEADER_FIELDS class attribute.

        """

        names = [field.name for field in self.image.get_header_fields()]
        self.assertEqual(names, self.HEADER_FIELDS)

    def test_update_fields_from_header(self):
        """
        Tests that :meth:`~django_dicom.models.dicom_entity.DicomEntity.update_fields_from_header`
        method returns the expected values. This test relies on the created instance's
        fields containing the expected values beforehand.

        """

        header = self.image.read_header()
        header_fields = self.image.get_header_fields()
        expected_values = {
            field.name: getattr(self.image, field.name) for field in header_fields
        }
        result = self.image.update_fields_from_header(header)
        self.assertIsNone(result)
        values = {
            field.name: getattr(self.image, field.name) for field in header_fields
        }
        self.assertDictEqual(values, expected_values)

    ##########
    # Fields #
    ##########

    # dcm
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

    # uid
    def test_uid_max_length(self):
        """
        DICOM's SOPInstanceUID_ attribute may only be as long as 64 characters (
        see the Unique Identifier (UI) `value-representation specification`).

        .. _SOPInstanceUID: https://dicom.innolitics.com/ciods/mr-image/sop-common/00080018
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.image._meta.get_field("uid")
        self.assertEqual(field.max_length, 64)

    def test_uid_is_unique(self):
        """
        Validates that the UID field is unique.

        """

        field = self.image._meta.get_field("uid")
        self.assertTrue(field.unique)

    def test_uid_validation(self):
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

    def test_uid_vebose_name(self):
        """
        Test the UID field vebose name.
        
        """

        field = self.image._meta.get_field("uid")
        self.assertEqual(field.verbose_name, "Image UID")

    # number
    def test_number_vebose_name(self):
        """
        Test the *number* field vebose name.
        
        """

        field = self.image._meta.get_field("number")
        self.assertEqual(field.verbose_name, "Image Number")

    # Others
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

    ###########
    # Methods #
    ###########

    def test_string(self):
        """
        Tests that the instance's :meth:`~django_dicom.models.image.Image.__str__`
        method returns its UID.
        For more information see `Django's str method documentation`_.
        
        """

        self.assertEqual(str(self.image), self.image.uid)

    def test_get_absolute_url(self):
        """
        Tests the :class:`~django_dicom.models.image.Image` model's `get_absolute_url`_
        method.
        
        .. _get_absolute_url: https://docs.djangoproject.com/en/2.2/ref/models/instances/#get-absolute-url
        """

        url = self.image.get_absolute_url()
        expected = f"/image/{self.image.id}/"
        self.assertEqual(url, expected)

    def test_read_file_method_return_type(self):
        """
        Tests that the :meth:`~django_dicom.models.image.Image.read_file` method
        return a :class:`~pydicom.dataset.FileDataset` instance.

        """

        dcm = self.image.read_file()
        self.assertIsInstance(dcm, pydicom.FileDataset)

    def test_read_file_configuration(self):
        """
        By default, the :meth:`django_dicom.models.image.Image.read_file` method
        is supposed to read the entire image (including the pixel array).

        """

        dcm = self.image.read_file()
        try:
            _ = dcm.pixel_array
        except AttributeError:
            self.fail("read_file() is supposed to load the image's pixel array!")

    def test_read_file_with_only_headers(self):
        """
        Tests the :meth:`django_dicom.models.image.Image.read_file` method
        *header_only* setting.
        
        """

        dcm = self.image.read_file(header_only=True)
        self.assertIsInstance(dcm, pydicom.FileDataset)
        with self.assertRaises(AttributeError):
            _ = dcm.pixel_array

    def test_get_data(self):
        """
        Tests the :meth:`django_dicom.models.image.Image.get_data` method returns
        the expected NumPy array.

        """

        data = self.image.get_data()
        self.assertIsInstance(data, np.ndarray)
        self.assertTupleEqual(data.shape, (512, 512))

    def test_read_header(self):
        """
        Tests that the :meth:`~django_dicom.models.image.Image.read_header` method
        returns the expected :class:`~django_dicom.reader.HeaderInformation` instance.

        """

        header = self.image.read_header()
        self.assertIsInstance(header, HeaderInformation)

    def test_get_b_value(self):
        """
        Tests the :meth:`~django_dicom.models.image.Image.get_b_value` method.
        Should return the B-value for DWI images and None for non-DWI images.
        TODO: Figure out why B-value seems to always be set to 0 for the DWI images.

        """

        self.assertIsNone(self.image.get_b_value())
        self.assertEqual(self.dwi_image.get_b_value(), 0)

    ##############
    # Properties #
    ##############

    def test_header(self):
        """
        Tests that the *_header* class attribute is properly updated by the
        :attr:`~django_dicom.models.image.Image.header` property.

        """

        self.assertIsNone(self.image._header)
        self.assertIsInstance(self.image.header, HeaderInformation)
        self.assertIsInstance(self.image._header, HeaderInformation)
        self.assertIs(self.image._header, self.image.header)

    def test_slice_timing(self):
        """
        Tests that the slice timing can be read for SIEMENS DICOM images.
        For more information see: https://en.wikibooks.org/wiki/SPM/Slice_Timing#Siemens_scanners.

        TODO: Extend to other vendors.

        """

        expected = DWI_SLICE_TIMING
        self.assertEqual(self.dwi_image.slice_timing, expected)

    def test_gradient_diretion(self):
        """
        Tests that the gradient direction can be read for SIEMENS DICOM images.
        For more information see: https://na-mic.org/wiki/NAMIC_Wiki:DTI:DICOM_for_DWI_and_DTI#Private_vendor:_Siemens.

        TODO: Extend to other vendors.

        """

        expected = [0.70710677, -0.70710677, 0.0]
        self.assertEqual(self.dwi_image.gradient_direction, expected)


DWI_SLICE_TIMING = [
    2460.0,
    0.0,
    1640.0,
    165.0,
    1805.0,
    327.5,
    1967.5,
    492.5,
    2132.5,
    655.0,
    2295.0,
    985.0,
    2625.0,
    1147.5,
    2787.5,
    1312.5,
    2952.5,
    1475.0,
    3115.0,
    820.0,
    2460.0,
    0.0,
    1640.0,
    165.0,
    1805.0,
    327.5,
    1967.5,
    492.5,
    2132.5,
    655.0,
    2295.0,
    985.0,
    2625.0,
    1147.5,
    2787.5,
    1312.5,
    2952.5,
    1475.0,
    3115.0,
    820.0,
    2460.0,
    0.0,
    1640.0,
    165.0,
    1805.0,
    327.5,
    1967.5,
    492.5,
    2132.5,
    655.0,
    2295.0,
    985.0,
    2625.0,
    1147.5,
    2787.5,
    1312.5,
    2952.5,
    1475.0,
    3115.0,
    820.0,
]
