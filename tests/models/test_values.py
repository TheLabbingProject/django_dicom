from django.test import TestCase
from tests.fixtures import TEST_PERSON_NAME  # , TEST_DATETIME
from django_dicom.models.values import PersonName
from django_dicom.utils.html import Html

# from django_dicom.models import DateTime


class PersonNameTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.values.person_name.PersonName` model.

    """

    @classmethod
    def setUpTestData(cls):
        PersonName.objects.create(**TEST_PERSON_NAME)

    def setUp(self):
        """
        Adds the created instances to the tests' contexts.
        For more information see unittest's :meth:`~unittest.TestCase.setUp` method.

        """
        self.person = PersonName.objects.last()

    def test_string(self):
        """
        Tests that the instance's :meth:`~django_dicom.models.values.PersonName.__str__`
        method returns the required pattern.
        For more information see `Django's str method documentation`_.

        """
        person_json = TEST_PERSON_NAME["value"]
        expected = f'{person_json["name_prefix"]} {person_json["given_name"]} {person_json["middle_name"]} {person_json["family_name"]} {person_json["name_suffix"]}'
        result = str(self.person)
        self.assertEqual(result, expected)

    def test_to_html(self):
        """
        Tests that the instance's :meth:`~django_dicom.models.values.PersonName.to_html`
        method returns the required pattern.

        """
        expected = Html.json(TEST_PERSON_NAME["value"])
        result = self.person.to_html()
        self.assertEqual(result, expected)


# class DateTimeTestCase(TestCase):
#     """
#     Tests for the :class:`~django_dicom.models.datetime.DateTime` model.

#     """

#     @classmethod
#     def setUpTestData(cls):
#         DateTime.objects.create(**TEST_DATETIME)

#     def setUp(self):
#         """
#         Adds the created instances to the tests' contexts.
#         For more information see unittest's :meth:`~unittest.TestCase.setUp` method.

#         """
#         self.datetime = DateTime.objects.last()

#     def test_string(self):
#         """
#         Tests that the instance's :meth:`~django_dicom.models.datetime.DateTime.__str__`
#         method returns the required pattern.
#         For more information see `Django's str method documentation`_.

#         """
#         expected = TEST_DATETIME["value"]
#         result = str(self.datetime)
#         self.assertEqual(result, expected)

#     def test_to_html(self):
#         """
#         Tests that the instance's :meth:`~django_dicom.models.values.PersonName.to_html`
#         method returns the required pattern.

#         """
#         expected = Html.json(TEST_DATETIME["value"])
#         result = self.datetime.to_html()
#         self.assertEqual(result, expected)
