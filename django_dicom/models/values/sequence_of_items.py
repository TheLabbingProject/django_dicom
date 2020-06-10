"""
Definition of the
:class:`~django_dicom.models.values.sequence_of_items.SequenceOfItems`
model.

"""

from django.utils.safestring import mark_safe
from django_dicom.models.managers.values.sequence_of_items import (
    SequenceOfItemsManager,
)
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.utils.html import Html


class SequenceOfItems(DataElementValue):
    """
    A :class:`django.db.models.Model` representing the value stored in a single
    :class:`~django_dicom.models.data_element.DataElement` with a value
    representation (VR) of *SQ*.

    *Sequence of Items* data elements are arrays of nested headers, and
    therefore this model does not override the
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.raw`
    and
    :attr:`~django_dicom.models.values.data_element_value.DataElementValue.value`
    field definitions (and so they remain *None*).
    """

    def to_html(self, verbose: bool = False, **kwargs) -> str:
        value = [
            subheader.to_html(verbose=verbose)
            for subheader in self.header_set.all()
        ]
        sep = Html.horizontal_line() if verbose else Html.BREAK
        return mark_safe(sep.join(value))

    objects = SequenceOfItemsManager()
