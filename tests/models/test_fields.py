"""
Tests for custom fields.

"""

from django.db.models import CharField
from django.forms import MultipleChoiceField
from django.test import TestCase
from django_dicom.models.fields import ChoiceArrayField


class ChoiceArrayFieldTestCase(TestCase):
    """
    Tests for the :class:`~django_dicom.models.fields.ChoiceArrayField` model.
    
    """

    # Some choices to test with:
    CHOICES = (("C1", "First Choice"), ("C2", "Second Choice"), ("C3", "Third Choice"))
    # For more information see:
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#choices

    def setUp(self):
        """
        Adds a :class:`~django_dicom.models.fields.ChoiceArrayField` instance to
        the tests' contexts.
        For more information see unittest's :meth:`~unittest.TestCase.setUp` method.
        
        """

        self.field = ChoiceArrayField(
            CharField(max_length=2, choices=self.CHOICES), size=3
        )

    def test_formfield_method(self):
        """
        Tests that :meth:`~django.db.models.Field.formfield` method returns the
        expected value.
        
        """

        choices = self.field.base_field.choices
        expected = {"form_class": MultipleChoiceField, "choices": choices}
        result = self.field.formfield()
        self.assertIsInstance(result, expected["form_class"])
        self.assertEqual(result.choices, list(expected["choices"]))
