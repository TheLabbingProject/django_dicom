"""
Custom :class:`~django.db.models.Field` sub-classes.
For more information see the `Django documentation`__.

__ https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#writing-custom-model-fields
"""

from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.
    Uses Django 1.9's postgres ArrayField and a MultipleChoiceField for its
    formfield.
    Based on this__ article.

    __ https://blogs.gnome.org/danni/2016/03/08/multiple-choice-using-djangos-postgres-arrayfield/

    """

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)
