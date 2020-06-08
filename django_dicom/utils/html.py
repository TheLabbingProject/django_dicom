import json

from django.urls import reverse
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter


ADMIN_VIEW_NAMES = {
    "DataElement": "admin:django_dicom_dataelement_change",
    "DataElementDefinition": "admin:django_dicom_dataelementdefinition_change",
    "DataElementValue": "admin:django_dicom_dataelementvalue_change",
    "Header": "admin:django_dicom_header_change",
    "Image": "admin:django_dicom_image_change",
    "Series": "admin:django_dicom_series_change",
    "Patient": "admin:django_dicom_patient_change",
    "Study": "admin:django_dicom_study_change",
}


class Html:
    BREAK = "<br>"
    HORIZONTAL_LINE = '<hr style="background-color: {color};">'

    @classmethod
    def admin_link(cls, model_name: str, pk: int, text: str = None) -> str:
        view_name = ADMIN_VIEW_NAMES.get(model_name)
        if view_name:
            url = reverse(view_name, args=(pk,))
            text = text if isinstance(text, str) else pk
            html = f'<a href="{url}">{text}</a>'
            return mark_safe(html)

    @classmethod
    def break_html(cls, pieces) -> str:
        return mark_safe(cls.BREAK.join(pieces))

    @classmethod
    def horizontal_line(cls, color: str = "black") -> str:
        return cls.HORIZONTAL_LINE.format(color=color)

    @classmethod
    def json(cls, value) -> json:
        response = json.dumps(value, sort_keys=True, indent=4, default=str)
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style>"
        return mark_safe(style + response)
