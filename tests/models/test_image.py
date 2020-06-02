import numpy as np

from dicom_parser.image import Image as DicomImage
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dicom.apps import DjangoDicomConfig
from django_dicom.models import Image, Series, Patient, Study, Header
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.utils import snake_case_to_camel_case
from tests.fixtures import (
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

    NON_HEADER_FIELDS = [
        "id",
        "dcm",
        "created",
        "modified",
        "series",
        "header",
        "warnings",
    ]
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
                self.assertTrue(
                    self.image.is_header_field(field), f"The field asserted is {field}"
                )

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

        header_fields = self.image.get_header_fields()
        expected_values = {
            field.name: getattr(self.image, field.name) for field in header_fields
        }
        result = self.image.update_fields_from_header(self.image.header)
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
            if field.name in ["id", "created", "modified", "date", "time"]:
                self.assertTrue(field.blank, f"{field.name} should be blankable!")
            elif field.name in ["number", "date", "time", "warnings", "series"]:
                self.assertTrue(field.null, f"{field.name} should not be nullable!")
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
        expected = f"/dicom/image/{self.image.id}/"
        self.assertEqual(url, expected)

    ##############
    # Properties #
    ##############

    def test_instance(self):
        """
        Tests that the `instance` property returns the appropriate
        :class:`~dicom_parser.image.Image` instance.

        """

        self.assertIsInstance(self.image.instance, DicomImage)

    def test_header(self):
        """
        Tests that the `header` property returns the
        :class:`~dicom_parser.image.Image` instance's
        associated :class:`~dicom_parser.header.Header` instance.

        """

        self.assertIsInstance(self.image.header, Header)

    def test_data(self):
        """
        Tests that the `data` property returns the
        :class:`~dicom_parser.image.Image` instance's data.

        """

        self.assertIsInstance(self.image.data, np.ndarray)
