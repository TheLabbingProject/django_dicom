from django.test import TestCase
from django_dicom.models import Image, Patient, Series, Study
from tests.fixtures import (TEST_IMAGE_FIELDS, TEST_PATIENT_FIELDS,
                            TEST_SERIES_FIELDS, TEST_STUDY_FIELDS)


class PatientTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.patient.Patient` model.

    """

    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to be used in the tests.
        For more information see Django's :class:`~django.test.TestCase`
        documentation_.

        .. _documentation:
           https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        """

        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(
            **TEST_PATIENT_FIELDS
        )
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        TEST_IMAGE_FIELDS["series"] = Series.objects.create(
            **TEST_SERIES_FIELDS
        )
        Image.objects.create(**TEST_IMAGE_FIELDS)

    def setUp(self):
        """
        Adds the created instances to the tests' contexts.
        For more information see unittest's :meth:`~unittest.TestCase.setUp` method.

        """

        self.image = Image.objects.get(uid=TEST_IMAGE_FIELDS["uid"])
        self.series = Series.objects.get(uid=TEST_SERIES_FIELDS["uid"])
        self.study = self.series.study
        self.patient = self.series.patient

    ##########
    # Fields #
    ##########

    # uid
    def test_uid_max_length(self):
        """
        DICOM's `Patient ID`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Patient ID: https://dicom.innolitics.com/ciods/mr-image/patient/00100020
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html

        """

        field = self.patient._meta.get_field("uid")
        self.assertEqual(field.max_length, 64)

    def test_uid_is_unique(self):
        """
        Validates that the *UID* field is unique.

        """

        field = self.patient._meta.get_field("uid")
        self.assertTrue(field.unique)

    def test_uid_verbose_name(self):
        """
        Test the *UID* field vebose name.

        """

        field = self.patient._meta.get_field("uid")
        self.assertEqual(field.verbose_name, "Patient UID")

    def test_uid_blank_and_null(self):
        """
        Every :class:`~django_dicom.models.patient.Patient` instance must have a UID.

        """

        field = self.patient._meta.get_field("uid")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    # date_of_birth
    def test_date_of_birth_blank_and_null(self):
        """
        The `Patient's Birth Date`_ attribute may be empty (`type 2 data element`_).

        .. _Patient's Birth Date: https://dicom.innolitics.com/ciods/mr-image/patient/00100030
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3

        """

        field = self.patient._meta.get_field("date_of_birth")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # sex
    def test_sex_max_length(self):
        """
        Tests that the sex field has the expected max_length.

        """

        field = self.patient._meta.get_field("sex")
        self.assertEqual(field.max_length, 1)

    def test_sex_blank_and_null(self):
        """
        The `Patient's Sex`_ attribute may be empty (`type 2 data element`_).

        .. _Patient's Sex: https://dicom.innolitics.com/ciods/mr-image/patient/00100040
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3

        """

        field = self.patient._meta.get_field("sex")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # name
    def test_name_blank_and_null(self):
        """
        Tests that the name fields are blankable and nullable according to the
        `Patient's Name`_ DICOM attribute definition (`type 2 data element`_).

        .. _Patient's Name: https://dicom.innolitics.com/ciods/mr-image/patient/00100010
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3

        """

        for field_name in Patient._NAME_PARTS:
            field = self.patient._meta.get_field(field_name)
            self.assertTrue(field.blank)
            self.assertTrue(field.null)

    def test_name_max_length(self):
        """
        Tests that the name fields has the expected max_length (see the Person
        Name (PN) `value-representation specification`_).

        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        """

        for field_name in Patient._NAME_PARTS:
            field = self.patient._meta.get_field(field_name)
            self.assertEqual(field.max_length, 64)

    ###########
    # Methods #
    ###########

    def test_string(self):
        """
        Tests that an :meth:`~django_dicom.models.patient.Patient.__str__` method returns
        its UID.
        For more information see `Django's str method documentation`_.

        .. _Django's str method documentation: https://docs.djangoproject.com/en/2.2/ref/models/instances/#str

        """

        self.assertEqual(str(self.patient), self.patient.uid)

    def test_get_absolute_url(self):
        """
        Tests the :meth:`~django_dicom.models.patient.Patient.get_absolute_url` method
        returns the expeted url.
        `More information`_

        .. _More information: https://docs.djangoproject.com/en/2.2/ref/models/instances/#get-absolute-url
        """

        url = self.patient.get_absolute_url()
        expected = f"/dicom/patient/{self.patient.id}/"
        self.assertEqual(url, expected)

    def test_get_full_name(self):
        """
        Tests that the :meth:`~django_dicom.models.patient.Patient.get_full_name`
        method returns "{given_name} {family_name}".

        """

        result = self.patient.get_full_name()
        expected = "Zvi Baratz"
        self.assertEqual(result, expected)

    def test_update_patient_name(self):
        """
        Tests patient name update according to the DICOM header `Patient's
        Name (PN)`_ data element fields.

        .. _Patient's Name (PN):
           http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html

        """

        self.patient.given_name = None
        self.patient.family_name = None
        self.patient.update_patient_name(self.image.header)
        self.assertEqual(self.patient.family_name, "Baratz")
        self.assertEqual(self.patient.given_name, "Zvi")
        self.assertEqual(self.patient.middle_name, "")
        self.assertEqual(self.patient.name_prefix, "")
        self.assertEqual(self.patient.name_suffix, "")

    def test_update_fields_from_header(self):
        """
        Tests that
        :meth:`~django_dicom.models.dicom_entity.DicomEntity.update_fields_from_header`
        method returns the expected values. This test relies on the created
        instance's fields containing the expected values beforehand.

        """

        header_fields = self.patient.get_header_fields()
        expected_values = {
            field.name: getattr(self.patient, field.name)
            for field in header_fields
        }
        result = self.patient.update_fields_from_header(self.image.header)
        self.assertIsNone(result)
        values = {
            field.name: getattr(self.patient, field.name)
            for field in header_fields
        }
        for key, value in values.items():
            try:
                self.assertEqual(value, expected_values[key])
            except AssertionError:
                if expected_values[key] is None:
                    self.assertEqual(value, "")
                else:
                    self.fail(
                        f"expected {expected_values[key]} but got {value}"
                    )

    def test_get_admin_link(self):
        """
        Tests that the
        :meth:`~django_dicom.models.dicom_entity.DicomEntity.get_admin_link`
        method returns the expected value.
        """

        namespace = "/admin/django_dicom/patient"
        url = f"{namespace}/{self.patient.id}/change/"
        expected = f'<a href="{url}">{self.patient.id}</a>'
        result = self.patient.get_admin_link()
        self.assertEqual(result, expected)

    ##############
    # Properties #
    ##############

    def test_admin_link(self):
        """
        Tests that the
        :attr:`~django_dicom.models.dicom_entity.DicomEntity.admin_link`
        property returns the expected value.
        """

        namespace = "/admin/django_dicom/patient"
        url = f"{namespace}/{self.patient.id}/change/"
        expected = f'<a href="{url}">{self.patient.id}</a>'
        result = self.patient.admin_link
        self.assertEqual(result, expected)
