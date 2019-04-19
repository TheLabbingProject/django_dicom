from django import forms


class CreateImagesForm(forms.Form):
    dcm_files = forms.FileField(
        label="DICOM files", widget=forms.ClearableFileInput(attrs={"multiple": True})
    )
