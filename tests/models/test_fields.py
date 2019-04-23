"""
Tests for custom fields.

"""

from django.db.models import CharField
from django.forms import MultipleChoiceField
from django.test import TestCase
from django_dicom.models.fields import ChoiceArrayField


class ChoiceArrayFieldTestCase(TestCase):
    CHOICES = (("C1", "First Choice"), ("C2", "Second Choice"), ("C3", "Third Choice"))

    def setUp(self):
        self.field = ChoiceArrayField(
            CharField(max_length=2, choices=self.CHOICES), size=3
        )

    def test_formfield_method(self):
        choices = self.field.base_field.choices
        expected = {"form_class": MultipleChoiceField, "choices": choices}
        result = self.field.formfield()
        self.assertIsInstance(result, expected["form_class"])
        self.assertEqual(result.choices, list(expected["choices"]))
