from django.test import TestCase
from django_dicom.models import DataElementDefinition
from tests.fixtures import (
    TEST_DATA_ELEMENT_DEFINITION,
    TEST_DATA_ELEMENT_DEFINITION2,
    TEST_DEFINITION_TO_SERIES,
    TEST_DEFINITION2_TO_SERIES,
)
import pandas as pd
from django.utils.safestring import mark_safe
from django.urls import reverse


class DataElementTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.data_element.DataElement` model.

    """

    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to test the :class:`~django_dicom.models.data_element_definition.DataElementDefinition`
        model.
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        """

        DataElementDefinition.objects.create(**TEST_DATA_ELEMENT_DEFINITION)
        DataElementDefinition.objects.create(**TEST_DATA_ELEMENT_DEFINITION2)

    def setUp(self):
        self.definition = DataElementDefinition.objects.last()
        self.definition2 = DataElementDefinition.objects.first()

    def test_string_long(self):
        expected = "\n" + pd.Series(TEST_DEFINITION_TO_SERIES).to_string()
        result = str(self.definition)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_string_person_name(self):
        expected = "\n" + pd.Series(TEST_DEFINITION2_TO_SERIES).to_string()
        result = str(self.definition2)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_dict_key_to_series_two_keywords(self):
        expected = "Value Representation"
        result = self.definition.dict_key_to_series("value_representation")
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_dict_key_to_series_one_keyword(self):
        expected = "Tag"
        result = self.definition.dict_key_to_series("tag")
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_to_series(self):
        expected = pd.Series(TEST_DEFINITION_TO_SERIES)
        result = self.definition.to_series()
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(result.all(), expected.all())

    def test_to_dict(self):
        expected = dict(TEST_DATA_ELEMENT_DEFINITION2)
        result = self.definition2.to_dict()
        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, expected)

    def test_admin_link(self):
        url = reverse(
            "admin:django_dicom_dataelementdefinition_change",
            args=(self.definition.id,),
        )
        text = str(tuple(self.definition.tag))
        html = f'<a href="{url}">{text}</a>'
        expected = mark_safe(html)
        result = self.definition.admin_link
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)
