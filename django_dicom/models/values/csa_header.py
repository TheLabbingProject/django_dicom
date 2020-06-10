"""
Definition of the
:class:`~django_dicom.models.values.csa_header.CsaHeader` model.
"""

from django.contrib.postgres.fields import JSONField
from django.db import models
from django_dicom.models.values.data_element_value import DataElementValue
from django_dicom.utils.html import Html


class CsaHeader(DataElementValue):
    """
    A :class:`~django.db.models.Model` representing a single Siemens' CSA
    header value.

    Hint
    ----
    For more information about CSA headers, see dicom_parser_\'s
    `CSA headers documentation`_.

    .. _dicom_parser: https://github.com/ZviBaratz/dicom_parser/
    .. _CSA headers documentation:
       https://dicom-parser.readthedocs.io/en/latest/siemens/csa_headers.html#csa-headers
    """

    raw = models.TextField(blank=True, null=True)
    value = JSONField(blank=True, null=True)

    def to_html(self, verbose: bool = False, **kwargs) -> str:
        """
        Returns the HTML representation of this instance.

        If the *verbose* keyword argument is passed as *True*, returns the
        entire header as JSON. Otherwise, returns an HTML link to this instance
        in the admin site.

        Parameters
        ----------
        verbose : bool, optional
            Whether to return all of the header information or just a link, by
            default False

        Returns
        -------
        str
            HTML text containing either JSON encoded header information or a
            link to the admin site
        """

        if verbose:
            return Html.json(self.value)
        text = f"Csa Header #{self.id}"
        return Html.admin_link("DataElementValue", self.id, text)
