from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dicom.models import Series, Patient, Study, Image
from tests.fixtures import (
    TEST_IMAGE_FIELDS,
    TEST_SERIES_FIELDS,
    TEST_STUDY_FIELDS,
    TEST_PATIENT_FIELDS,
)


class SeriesTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.study.Study` model.
    
    """

    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to be used in the tests.
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase

        """

        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(**TEST_PATIENT_FIELDS)
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        TEST_IMAGE_FIELDS["series"] = Series.objects.create(**TEST_SERIES_FIELDS)
        Image.objects.create(**TEST_IMAGE_FIELDS)

    def setUp(self):
        """
        Adds the created instances to the tests' contexts.
        For more information see unittest's :meth:`~unittest.TestCase.setUp` method.

        """

        self.image = Image.objects.get(uid=TEST_IMAGE_FIELDS["uid"])
        self.series = Series.objects.get(uid=TEST_SERIES_FIELDS["uid"])
        self.study = self.series.study

    ########
    # Meta #
    ########

    def test_study_verbose_name_plural(self):
        """
        Validate the `verbose name plural`_ ("Studies") of the :class:`~django_dicom.models.study.Study` model.

        .. _verbose name plural: https://docs.djangoproject.com/en/2.2/ref/models/options/#verbose-name-plural       
        """

        self.assertEqual(Study._meta.verbose_name_plural, "Studies")

    ##########
    # Fields #
    ##########

    # uid
    def test_uid_max_length(self):
        """
        DICOM's `Study Instance UID`_ attribute may only be as long as 64 characters (
        see the Unique Identifier (UI) `value-representation specification`).

        .. _Study Instance UID: https://dicom.innolitics.com/ciods/mr-image/general-study/0020000d
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.study._meta.get_field("uid")
        self.assertEqual(field.max_length, 64)

    def test_uid_is_unique(self):
        """
        Validates that the *UID* field is unique.

        """

        field = self.study._meta.get_field("uid")
        self.assertTrue(field.unique)

    def test_uid_validation(self):
        """
        An :class:`~django_dicom.models.study.Study` instance *UID* field may only
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
        uid = self.study.uid
        for character in non_digit_or_dot_chars:
            self.study.uid = character + uid[1:]
            with self.assertRaises(ValidationError):
                self.study.full_clean()
        self.study.uid = uid

    def test_uid_vebose_name(self):
        """
        Test the *UID* field vebose name.
        
        """

        field = self.study._meta.get_field("uid")
        self.assertEqual(field.verbose_name, "Study UID")

    def test_uid_blank_and_null(self):
        """
        Every :class:`~django_dicom.models.study.Study` instance must have a UID.

        """

        field = self.study._meta.get_field("uid")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    # description
    def test_description_max_length(self):
        """
        DICOM's `Study Description`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Study Description: https://dicom.innolitics.com/ciods/mr-image/general-study/00081030
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.study._meta.get_field("description")
        self.assertEqual(field.max_length, 64)

    def test_description_blank_and_null(self):
        """
        The `Study Description`_ attribute is optional (`type 3 data element`).

        .. _Study Description: https://dicom.innolitics.com/ciods/mr-image/general-study/00081030
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.study._meta.get_field("description")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # date
    def test_date_blank_and_null(self):
        """
        The `Study Date`_ attribute may be empty (`type 2 data element`).

        .. _Study Date: https://dicom.innolitics.com/ciods/mr-image/general-study/00080020
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.study._meta.get_field("date")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # time
    def test_time_blank_and_null(self):
        """
        The `Study Time`_ attribute may be empty (`type 2 data element`).

        .. _Study Time: https://dicom.innolitics.com/ciods/mr-image/general-study/00080030
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.study._meta.get_field("time")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    ###########
    # Methods #
    ###########

    def test_string(self):
        """
        Tests that an :meth:`~django_dicom.models.study.Study.__str__` method returns
        its UID.
        For more information see `Django's str method documentation`_.

        """

        self.assertEqual(str(self.study), self.study.uid)

    def test_get_absolute_url(self):
        """
        Tests the :meth:`~django_dicom.models.study.Study.get_absolute_url` method
        returns the expeted url.
        For more information regarding `get_absolute_url` see `the Django documentation`_.
        
        .. _the Django documentation: https://docs.djangoproject.com/en/2.2/ref/models/instances/#get-absolute-url
        """

        url = self.study.get_absolute_url()
        expected = f"/study/{self.study.id}/"
        self.assertEqual(url, expected)

    def test_update_fields_from_header(self):
        """
        Tests that :meth:`~django_dicom.models.dicom_entity.DicomEntity.update_fields_from_header`
        method returns the expected values. This test relies on the created instance's
        fields containing the expected values beforehand.

        """

        header = self.image.read_header()
        header_fields = self.study.get_header_fields()
        expected_values = {
            field.name: getattr(self.study, field.name) for field in header_fields
        }
        result = self.study.update_fields_from_header(header)
        self.assertIsNone(result)
        values = {
            field.name: getattr(self.study, field.name) for field in header_fields
        }
        self.assertDictEqual(values, expected_values)
