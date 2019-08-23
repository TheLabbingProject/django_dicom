import numpy as np
import os

from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dicom.models import Series, Patient, Study, Image
from django_dicom.reader.code_strings import (
    Modality,
    PatientPosition,
    ScanningSequence,
    SequenceVariant,
)
from tests.fixtures import (
    TEST_IMAGE_PATH,
    TEST_DWI_IMAGE_PATH,
    TEST_IMAGE_FIELDS,
    TEST_DWI_IMAGE_FIELDS,
    TEST_SERIES_FIELDS,
    TEST_DWI_SERIES_FIELDS,
    TEST_STUDY_FIELDS,
    TEST_PATIENT_FIELDS,
)


class SeriesTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.series.Series` model.
    
    """

    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to be used in the tests.
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

    ########
    # Meta #
    ########

    def test_series_verbose_name_plural(self):
        """
        Validate the `verbose name plural`_ ("`Series`_") of the :class:`~django_dicom.models.series.Series` model.

        .. _verbose name plural: https://docs.djangoproject.com/en/2.2/ref/models/options/#verbose-name-plural
        .. _Series: https://en.wiktionary.org/wiki/series        
        """

        self.assertEqual(Series._meta.verbose_name_plural, "Series")

    def test_series_ordering(self):
        """
        Validate the `ordering`_ of the :class:`~django_dicom.models.series.Series` model.

        .. _ordering: https://docs.djangoproject.com/en/2.2/ref/models/options/#ordering
        .. _Series: https://en.wiktionary.org/wiki/series        
        """

        self.assertTupleEqual(Series._meta.ordering, ("number",))

    # TODO: Test for indexes

    ##########
    # Fields #
    ##########

    # uid
    def test_uid_max_length(self):
        """
        DICOM's SeriesInstanceUID_ attribute may only be as long as 64 characters (
        see the Unique Identifier (UI) `value-representation specification`).

        .. _SeriesInstanceUID: https://dicom.innolitics.com/ciods/mr-image/general-series/0020000e
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.series._meta.get_field("uid")
        self.assertEqual(field.max_length, 64)

    def test_uid_is_unique(self):
        """
        Validates that the *UID* field is unique.

        """

        field = self.series._meta.get_field("uid")
        self.assertTrue(field.unique)

    def test_uid_validation(self):
        """
        An :class:`~django_dicom.models.series.Series` instance *UID* field may only
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
        uid = self.series.uid
        for character in non_digit_or_dot_chars:
            self.series.uid = character + uid[1:]
            with self.assertRaises(ValidationError):
                self.series.full_clean()
        self.series.uid = uid

    def test_uid_verbose_name(self):
        """
        Test the *UID* field vebose name.
        
        """

        field = self.series._meta.get_field("uid")
        self.assertEqual(field.verbose_name, "Series UID")

    def test_uid_blank_and_null(self):
        """
        Every :class:`~django_dicom.models.series.Series` instance must have a UID.

        """

        field = self.series._meta.get_field("uid")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    # number
    def test_number_vebose_name(self):
        """
        Test the *number* field vebose name.
        
        """

        field = self.series._meta.get_field("number")
        self.assertEqual(field.verbose_name, "Series Number")

    def test_number_blank_and_null(self):
        """
        The `Series Number`_ attribute may be empty (`type 2 data element`).

        .. _Series Number: https://dicom.innolitics.com/ciods/mr-image/general-series/00200011
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.series._meta.get_field("number")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # description
    def test_description_max_length(self):
        """
        DICOM's `Series Description`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Series Description: https://dicom.innolitics.com/ciods/mr-image/general-series/00200011
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.series._meta.get_field("description")
        self.assertEqual(field.max_length, 64)

    def test_description_blank_and_null(self):
        """
        The `Series Description`_ attribute may be empty (`type 2 data element`).

        .. _Series Description: https://dicom.innolitics.com/ciods/mr-image/general-series/00200011
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.series._meta.get_field("description")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_description_vebose_name(self):
        """
        Test the *description* field vebose name.
        
        """

        field = self.series._meta.get_field("description")
        self.assertEqual(field.verbose_name, "Series Description")

    # date
    def test_date_blank_and_null(self):
        """
        The `Series Date`_ attribute is optional (`type 3 data element`).

        .. _Series Date: https://dicom.innolitics.com/ciods/mr-image/general-series/00080021
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.series._meta.get_field("date")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # time
    def test_time_blank_and_null(self):
        """
        The `Series Time`_ attribute is optional (`type 3 data element`).

        .. _Series Time: https://dicom.innolitics.com/ciods/mr-image/general-series/00080031
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.series._meta.get_field("time")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # echo_time
    def test_echo_time_blank_and_null(self):
        """
        The `Echo Time`_ attribute may be empty (`type 2 data element`).

        .. _Echo Time: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180081
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.series._meta.get_field("echo_time")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_echo_time_positive_float_validation(self):
        """
        The `Echo Time`_ attribute measures time in milliseconds and therefore must
        be positive.

        .. _Echo Time: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180081

        """
        value = self.series.echo_time
        self.series.echo_time = -0.4
        with self.assertRaises(ValidationError):
            self.series.full_clean()
        self.series.echo_time = value

    # inversion_time
    def test_inversion_time_blank_and_null(self):
        """
        The `Inversion Time`_ attribute may be empty (`type 2C data element`).

        .. _Inversion Time: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180082
        .. _type 2C data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.4
        
        """

        field = self.series._meta.get_field("inversion_time")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_inversion_time_positive_float_validation(self):
        """
        The `Inversion Time`_ attribute measures time in milliseconds and therefore must
        be positive.

        .. _Inversion Time: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180082        

        """
        value = self.series.inversion_time
        self.series.inversion_time = -0.4
        with self.assertRaises(ValidationError):
            self.series.full_clean()
        self.series.inversion_time = value

    # repetition_time
    def test_repetition_time_blank_and_null(self):
        """
        The `Repetition Time`_ attribute may be empty (`type 2C data element`).

        .. _Repetition Time: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180080
        .. _type 2C data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.4
        
        """

        field = self.series._meta.get_field("repetition_time")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_repetition_time_positive_float_validation(self):
        """
        The `Repetition Time`_ attribute measures time in milliseconds and therefore must
        be positive.

        .. _Repetition Time: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180080       

        """
        value = self.series.repetition_time
        self.series.repetition_time = -0.4
        with self.assertRaises(ValidationError):
            self.series.full_clean()
        self.series.repetition_time = value

    # scanning_sequence
    def test_scanning_sequence_blank_and_null(self):
        """
        The `Scanning Sequence`_ attribute may not be empty (`type 1 data element`).

        .. _Scanning Sequence: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180020
        .. _type 1 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.1
        
        """

        field = self.series._meta.get_field("scanning_sequence")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_scanning_sequence_base_max_length(self):
        """
        `Scanning Sequence`_ definitions are 2 characters long.

        .. _Scanning Sequence: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180020
        
        """

        field = self.series._meta.get_field("scanning_sequence")
        self.assertEqual(field.base_field.max_length, 2)

    def test_scanning_sequence_size(self):
        """
        The `Scanning Sequence`_ attribute has five possible values, with some of 
        them actually being mutually exclusive. We're limiting to five in any case.

        .. _Scanning Sequence: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180020
        
        """

        field = self.series._meta.get_field("scanning_sequence")
        self.assertEqual(field.size, 5)

    def test_scanning_sequence_base_choices(self):
        """
        `Scanning Sequence`_ is a `Code String (CS)`_ data element and therfores
        has a limited number of possible values.

        .. _Scanning Sequence: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180020
        .. _Code String (CS): http://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html
        
        """

        field = self.series._meta.get_field("scanning_sequence")
        self.assertEqual(field.base_field.choices, ScanningSequence.choices())

    # sequence_variant
    def test_sequence_variant_blank_and_null(self):
        """
        The `Sequence Variant`_ attribute may not be empty (`type 1 data element`).

        .. _Sequence Variant: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180021
        .. _type 1 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.1
        
        """

        field = self.series._meta.get_field("scanning_sequence")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_sequence_variant_base_max_length(self):
        """
        `Sequence Variant`_ definitions can be 4 characters long.

        .. _Sequence Variant: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180021
        
        """

        field = self.series._meta.get_field("sequence_variant")
        self.assertEqual(field.base_field.max_length, 4)

    def test_sequence_variant_size(self):
        """
        The `Sequence Variant`_ attribute has eight possible values, with some of 
        them actually being mutually exclusive and also including NONE. We're 
        limiting to six just in case.

        .. _Sequence Variant: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180021
        
        """

        field = self.series._meta.get_field("sequence_variant")
        self.assertEqual(field.size, 6)

    def test_sequence_variant_base_choices(self):
        """
        `Sequence Variant`_ is a `Code String (CS)`_ data element and therfores
        has a limited number of possible values.

        .. _Sequence Variant: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180021
        .. _Code String (CS): http://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html
        
        """

        field = self.series._meta.get_field("sequence_variant")
        self.assertEqual(field.base_field.choices, SequenceVariant.choices())

    # pixel_spacing
    def test_pixel_spacing_blank_and_null(self):
        """
        The `Pixel Spacing`_ attribute may not be empty (`type 1 data element`).

        .. _Pixel Spacing: https://dicom.innolitics.com/ciods/mr-image/image-plane/00280030
        .. _type 1 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.1
        
        """

        field = self.series._meta.get_field("pixel_spacing")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_pixel_spacing_size(self):
        """
        The `Pixel Spacing`_ attribute specifies the distance between the centers
        of two adjacent pixels in the *row* (X) and *column* (Y) dimensions.

        .. _Pixel Spacing: https://dicom.innolitics.com/ciods/mr-image/image-plane/00280030
        """

        field = self.series._meta.get_field("pixel_spacing")
        self.assertEqual(field.size, 2)

    def test_pixel_spacing_positive_float_validation(self):
        """
        The `Pixel Spacing`_ attribute specifies distances in millimeters, and
        therefore must be positive.

        .. _Pixel Spacing: https://dicom.innolitics.com/ciods/mr-image/image-plane/00280030
        """

        invalid_values = [(-0.7, 1), (0.4, -0.9), (-1, -2.0)]
        original_value = self.series.pixel_spacing
        for value in invalid_values:
            self.series.pixel_spacing = value
            with self.assertRaises(ValidationError):
                self.series.full_clean()
        self.series.pixel_spacing = original_value

    # manufacturer
    def test_manufacturer_blank_and_null(self):
        """
        The `Manufacturer`_ attribute may be empty (`type 2 data element`).

        .. _Manufacturer: https://dicom.innolitics.com/ciods/mr-image/general-equipment/00080070
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.series._meta.get_field("manufacturer")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_manufacturer_max_length(self):
        """
        DICOM's `Manufacturer`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Manufacturer: https://dicom.innolitics.com/ciods/mr-image/general-equipment/00080070
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """

        field = self.series._meta.get_field("manufacturer")
        self.assertEqual(field.max_length, 64)

    # manufacturer_model
    def test_manufacturer_model_name_blank_and_null(self):
        """
        The `Manufacturer's Model Name`_ attribute is optional (`type 3 data element`).

        .. _Manufacturer's Model Name: https://dicom.innolitics.com/ciods/mr-image/general-series/00080021
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.series._meta.get_field("manufacturer_model_name")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_manufacturer_model_name_max_length(self):
        """
        DICOM's `Manufacturer's Model Name`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Manufacturer's Model Name: https://dicom.innolitics.com/ciods/mr-image/general-series/00080021
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """
        field = self.series._meta.get_field("manufacturer_model_name")
        self.assertEqual(field.max_length, 64)

    # magnetic_field_strength
    def test_magnetic_field_strengh_blank_and_null(self):
        """
        The `Magnetic Field Strength`_ attribute is optional (`type 3 data element`).

        .. _Magnetic Field Strength: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180087
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.series._meta.get_field("magnetic_field_strength")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_magnetic_field_strength_positive_float_validation(self):
        """
        The `Magnetic Field Strength`_ attribute measures field strength in `Tesla (T)`_
        and therefore must be positive.
        
        .. _Magnetic Field Strength: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180087
        .. _Tesla (T): https://en.wikipedia.org/wiki/Tesla_(unit)

        """
        value = self.series.magnetic_field_strength
        self.series.magnetic_field_strength = -3.0
        with self.assertRaises(ValidationError):
            self.series.full_clean()
        self.series.magnetic_field_strength = value

    # device_serial_number
    def test_device_serial_number_blank_and_null(self):
        """
        The `Device Serial Number`_ attribute is optional (`type 3 data element`).

        .. _Device Serial Number: https://dicom.innolitics.com/ciods/mr-image/general-equipment/00181000
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.series._meta.get_field("device_serial_number")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_device_serial_number_max_length(self):
        """
        DICOM's `Device Serial Number`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Device Serial Number: https://dicom.innolitics.com/ciods/mr-image/general-equipment/00181000
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """
        field = self.series._meta.get_field("device_serial_number")
        self.assertEqual(field.max_length, 64)

    # body_part_examined
    def test_body_part_examined_blank_and_null(self):
        """
        The `Body Part Examined`_ attribute is optional (`type 3 data element`).

        .. _Body Part Examined: https://dicom.innolitics.com/ciods/mr-image/general-series/00180015
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        
        """

        field = self.series._meta.get_field("body_part_examined")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_body_part_examined_max_length(self):
        """
        DICOM's `Body Part Examined`_ attribute may only be as long as 16 characters (
        see the Code String (CS) `value-representation specification`).

        .. _Body Part Examined: https://dicom.innolitics.com/ciods/mr-image/general-series/00180015
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        
        """
        field = self.series._meta.get_field("body_part_examined")
        self.assertEqual(field.max_length, 16)

    # patient_position
    def test_patient_position_blank_and_null(self):
        """
        The `Patient Position`_ attribute may be empty (`type 2C data element`).

        .. _Patient Position: https://dicom.innolitics.com/ciods/mr-image/general-series/00185100
        .. _type 2C data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.4
        
        """

        field = self.series._meta.get_field("patient_position")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_patient_position_max_length(self):
        """
        DICOM's `Patient Position`_ attribute may only be as long as 4 characters.

        .. _Patient Position: https://dicom.innolitics.com/ciods/mr-image/general-series/00185100
        """
        field = self.series._meta.get_field("patient_position")
        self.assertEqual(field.max_length, 4)

    def test_patient_position_choices(self):
        """
        `Patient Position`_ is a `Code String (CS)`_ data element and therfores
        has a limited number of possible values.

        .. _Patient Position: https://dicom.innolitics.com/ciods/mr-image/general-series/00185100
        .. _Code String (CS): http://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html
        
        """

        field = self.series._meta.get_field("patient_position")
        self.assertEqual(field.choices, PatientPosition.choices())

    # modality
    def test_modality_blank_and_null(self):
        """
        The `Modality`_ attribute may not be empty (`type 1 data element`).

        .. _Modality: https://dicom.innolitics.com/ciods/mr-image/general-series/00080060
        .. _type 1 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.1
        
        """

        field = self.series._meta.get_field("modality")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_modality_max_length(self):
        """
        DICOM's `Modality`_ attribute may only be as long as 10 characters.

        .. _Modality: https://dicom.innolitics.com/ciods/mr-image/general-series/00080060
        """
        field = self.series._meta.get_field("modality")
        self.assertEqual(field.max_length, 10)

    def test_modality_choices(self):
        """
        `Modality`_ is a `Code String (CS)`_ data element and therfores
        has a limited number of possible values.

        .. _Modality: https://dicom.innolitics.com/ciods/mr-image/general-series/00080060
        .. _Code String (CS): http://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html
        """

        field = self.series._meta.get_field("modality")
        self.assertEqual(field.choices, Modality.choices())

    # institution_name
    def test_institution_name_blank_and_null(self):
        """
        The `Institution Name`_ attribute is optional (`type 3 data element`).

        .. _Institution Name: https://dicom.innolitics.com/ciods/mr-image/general-equipment/00080080
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        """

        field = self.series._meta.get_field("institution_name")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_institution_name_max_length(self):
        """
        DICOM's `Institution Name`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Institution Name: https://dicom.innolitics.com/ciods/mr-image/general-equipment/00080080
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
        """

        field = self.series._meta.get_field("institution_name")
        self.assertEqual(field.max_length, 64)

    # protocol_name
    def test_protocol_name_blank_and_null(self):
        """
        The `Protocol Name`_ attribute is optional (`type 3 data element`).

        .. _Protocol Name: https://dicom.innolitics.com/ciods/mr-image/general-series/00181030
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        """

        field = self.series._meta.get_field("protocol_name")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_protocol_name_max_length(self):
        """
        DICOM's `Protocol Name`_ attribute may only be as long as 64 characters (
        see the Long String (LO) `value-representation specification`).

        .. _Protocol Name: https://dicom.innolitics.com/ciods/mr-image/general-series/00181030
        .. _value-representation specification: http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html        
        """

        field = self.series._meta.get_field("protocol_name")
        self.assertEqual(field.max_length, 64)

    # flip_angle
    def test_flip_angle_blank_and_null(self):
        """
        The `Flip Angle`_ attribute is optional (`type 3 data element`).

        .. _Flip Angle: https://dicom.innolitics.com/ciods/mr-image/mr-image/00181314
        .. _type 3 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.5
        """

        field = self.series._meta.get_field("flip_angle")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    # mr_acquisition_type
    def test_mr_acquisition_type_max_length(self):
        """
        DICOM's `MR Acquisition Type`_ attribute may only be as long as 2 characters.

        .. _MR Acquisition Type: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180023
        """

        field = self.series._meta.get_field("mr_acquisition_type")
        self.assertEqual(field.max_length, 2)

    def test_mr_acquisition_type_choices(self):
        """
        `MR Acquisition Type`_ is a `Code String (CS)`_ data element and therfores
        has a limited number of possible values.

        .. _MR Acquisition Type: https://dicom.innolitics.com/ciods/mr-image/mr-image/00180023
        .. _Code String (CS): http://northstar-www.dartmouth.edu/doc/idl/html_6.2/Value_Representations.html\        
        """

        choices = (("2D", "2D"), ("3D", "3D"))
        field = self.series._meta.get_field("mr_acquisition_type")
        self.assertEqual(field.choices, choices)

    # slice thickness
    def test_slice_thickness_blank_and_null(self):
        """
        The `Slice Thickness`_ attribute may be empty (`type 2 data element`).

        .. _Slice Thickness: https://dicom.innolitics.com/ciods/mr-image/image-plane/00180050
        .. _type 2 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.3
        
        """

        field = self.series._meta.get_field("slice_thickness")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_slice_thickness_positive_float_validation(self):
        """
        The `Slice Thickness`_ attribute measures thickness in millimeters and therefore must
        be positive.

        .. _Slice Thickness: https://dicom.innolitics.com/ciods/mr-image/image-plane/00180050

        """
        value = self.series.slice_thickness
        self.series.slice_thickness = -0.4
        with self.assertRaises(ValidationError):
            self.series.full_clean()
        self.series.slice_thickness = value

    # study
    def test_study_blank_and_null(self):
        """
        The `Study Instance UID`_ attribute may not be empty (`type 1 data element`)
        and therefore every series must have a study.

        .. _Study Instance UID: https://dicom.innolitics.com/ciods/mr-image/general-study/0020000d
        .. _type 1 data element: http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.4.html#sect_7.4.1     
        """

        field = self.series._meta.get_field("study")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    # patient
    def test_patient_blank_and_null(self):
        """
        DICOM's Patient attributes are all either conditionally required or nullable,
        and therefore it is possible for the patient relationship to be unused.
        
        """

        field = self.series._meta.get_field("patient")
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    ###########
    # Methods #
    ###########

    def test_string(self):
        """
        Tests that an :class:`~django_dicom.models.series.Series` instance's str
        method returns its UID.
        For more information see `Django's str method documentation`_.

        """

        self.assertEqual(str(self.series), self.series.uid)
        self.assertEqual(str(self.dwi_series), self.dwi_series.uid)

    def test_get_absolute_url(self):
        """
        Tests the :class:`~django_dicom.models.series.Series` model's `get_absolute_url`_
        method.
        
        .. _get_absolute_url: https://docs.djangoproject.com/en/2.2/ref/models/instances/#get-absolute-url
        """
        for sample_series in (self.series, self.dwi_series):
            url = sample_series.get_absolute_url()
            expected = f"/series/{sample_series.id}/"
            self.assertEqual(url, expected)

    def test_update_fields_from_header(self):
        """
        Tests that :meth:`~django_dicom.models.dicom_entity.DicomEntity.update_fields_from_header`
        method returns the expected values. This test relies on the created instance's
        fields containing the expected values beforehand.

        """

        header = self.image.read_header()
        header_fields = self.series.get_header_fields()
        expected_values = {
            field.name: getattr(self.series, field.name) for field in header_fields
        }
        result = self.series.update_fields_from_header(header)
        self.assertIsNone(result)
        values = {
            field.name: getattr(self.series, field.name) for field in header_fields
        }
        for key, value in values.items():
            if expected_values[key] != value:
                print(f"{key} expected {expected_values[key]} but got {value}")
        self.assertDictEqual(values, expected_values)

    def test_get_data(self):
        """
        Tests retrieving the series data from the model. 
        In this case we only have one instance for each series so the third dimension's
        size will be 1.
        
        """

        # Test localizer series
        data = self.series.get_data()
        self.assertIsInstance(data, np.ndarray)
        self.assertTupleEqual(data.shape, (512, 512, 1))
        # Test DWI series
        dwi_data = self.dwi_series.get_data()
        self.assertIsInstance(dwi_data, np.ndarray)
        self.assertTupleEqual(dwi_data.shape, (704, 704, 1))

    def test_get_path(self):
        """
        Tests the :meth:`~django_dicom.models.series.Series.get_path` method
        returns the series base directory.
        
        """

        # Test localizer series
        expected = os.path.dirname(TEST_IMAGE_PATH)
        result = self.series.get_path()
        self.assertEqual(result, expected)
        # Test DWI series
        expected = os.path.dirname(TEST_DWI_IMAGE_PATH)
        result = self.dwi_series.get_path()
        self.assertEqual(result, expected)

    def test_get_scanning_sequence_display(self):
        """
        Tests the :meth:`~django_dicom.models.series.Series.get_scanning_sequence_display`
        method returns the expected value for the given series.
        
        """

        # Test localizer series
        result = self.series.get_scanning_sequence_display()
        expected = ["Gradient Recalled"]
        self.assertListEqual(result, expected)
        # Test DWI series
        result = self.dwi_series.get_scanning_sequence_display()
        expected = ["Echo Planar"]
        self.assertListEqual(result, expected)

    def test_get_sequence_variant_display(self):
        """
        Tests the :meth:`~django_dicom.models.series.Series.get_sequence_variant_display`
        method returns the expected value for the given series.
        
        """

        # Test localizer series
        result = self.series.get_sequence_variant_display()
        expected = ["Spoiled", "Oversampling Phase"]
        self.assertListEqual(result, expected)
        # Test DWI series
        result = self.dwi_series.get_sequence_variant_display()
        expected = ["Segmented k-Space", "Spoiled"]
        self.assertListEqual(result, expected)

    def test_get_gradient_directions(self):
        """
        Tests the :meth:`~django_dicom.models.series.Series.get_gradient_directions`
        method returns the expected value for the given series.
        
        """

        # Test localizer series (no gradient directions, should return None)
        result = self.series.get_gradient_directions()
        self.assertIsNone(result)
        # Test DWI image
        result = self.dwi_series.get_gradient_directions()
        expected = [[0.70710677], [-0.70710677], [0.0]]
        self.assertListEqual(result, expected)

        # Test unsupported manufacturer raises NotImplementedError
        self.series.manufacturer = "MAGNETO"
        with self.assertRaises(NotImplementedError):
            self.series.get_gradient_directions()

