import pandas as pd
from django.test import TestCase
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_dicom.models import DataElement, DataElementDefinition, Header
from django_dicom.models.values import LongString, PersonName
from tests.fixtures import (TEST_DATA_ELEMENT, TEST_DATA_ELEMENT2,
                            TEST_DATA_ELEMENT_DEFINITION,
                            TEST_DATA_ELEMENT_DEFINITION2,
                            TEST_DATA_ELEMENT_SERIES,
                            TEST_DATA_ELEMENT_VALUE_LONG_STRING,
                            TEST_PERSON_NAME, TEST_PERSON_NAME2)


class DataElementTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.data_element.DataElement` model.

    """

    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to test the :class:`~django_dicom.models.data_element.DataElement`
        model.
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        """
        TEST_DATA_ELEMENT["header"] = Header.objects.create()
        TEST_DATA_ELEMENT2["header"] = TEST_DATA_ELEMENT["header"]

        TEST_DATA_ELEMENT["definition"] = DataElementDefinition.objects.create(
            **TEST_DATA_ELEMENT_DEFINITION
        )
        TEST_DATA_ELEMENT2["definition"] = DataElementDefinition.objects.create(
            **TEST_DATA_ELEMENT_DEFINITION2
        )

        value = LongString.objects.create(**TEST_DATA_ELEMENT_VALUE_LONG_STRING)
        value1 = PersonName.objects.create(**TEST_PERSON_NAME)
        value2 = PersonName.objects.create(**TEST_PERSON_NAME2)

        element = DataElement.objects.create(**TEST_DATA_ELEMENT)
        element2 = DataElement.objects.create(**TEST_DATA_ELEMENT2)

        element._values.add(value)
        element2._values.add(value1)
        element2._values.add(value2)
        TEST_DATA_ELEMENT_SERIES["Value"] = element.value

    def setUp(self):
        self.element = DataElement.objects.last()
        self.element2 = DataElement.objects.first()

    def test_string(self):
        expected = "\n" + pd.Series(TEST_DATA_ELEMENT_SERIES).to_string()
        result = str(self.element)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_to_html(self):
        expected = "SIEMENS CSA NON-IMAGE"
        result = self.element.to_html()
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test__normalize_dict_key_two_keywords(self):
        expected = "Value Representation"
        result = self.element._normalize_dict_key("value_representation")
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test__normalize_dict_key_one_keyword(self):
        expected = "Tag"
        result = self.element._normalize_dict_key("tag")
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_to_verbose_series(self):
        expected = pd.Series(TEST_DATA_ELEMENT_SERIES)
        result = self.element.to_verbose_series()
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(result.all(), expected.all())

    def test_to_verbose_dict(self):
        expected = dict(TEST_DATA_ELEMENT_DEFINITION)
        del expected["description"]
        expected["value"] = self.element.value
        result = self.element.to_verbose_dict()
        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, expected)

    def test_value_single(self):
        expected = TEST_DATA_ELEMENT_VALUE_LONG_STRING["value"]
        result = self.element.value
        self.assertEqual(result, expected)

    def test_value_multiple(self):
        expected = [TEST_PERSON_NAME["value"], TEST_PERSON_NAME2["value"]]
        result = self.element2.value
        self.assertEqual(result, expected)
        self.assertListEqual(result, expected)

    def test_value_multiplicity_single(self):
        expected = 1
        result = self.element.value_multiplicity
        self.assertIsInstance(result, int)
        self.assertEqual(result, expected)

    def test_value_multiplicity_multiple(self):
        expected = 2
        result = self.element2.value_multiplicity
        self.assertIsInstance(result, int)
        self.assertEqual(result, expected)

    def test_admin_link(self):
        url = reverse("admin:django_dicom_dataelement_change", args=(self.element.id,))
        html = f'<a href="{url}">{self.element.id}</a>'
        expected = mark_safe(html)
        result = self.element.admin_link
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)
