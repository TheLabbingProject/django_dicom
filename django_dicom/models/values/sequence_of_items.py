from django.utils.safestring import mark_safe
from django_dicom.models.managers.values.sequence_of_items import SequenceOfItemsManager
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.utils.html import Html


class SequenceOfItems(DataElementValue):
    def to_html(self, verbose: bool = False, **kwargs) -> str:
        value = [
            subheader.to_html(verbose=verbose) for subheader in self.header_set.all()
        ]
        sep = Html.horizontal_line() if verbose else Html.BREAK
        return mark_safe(sep.join(value))

    objects = SequenceOfItemsManager()
