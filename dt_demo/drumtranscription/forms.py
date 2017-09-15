from django import forms
from .validators import validate_file_extension


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file', validators=[validate_file_extension], required=True
    )


class YoutubeForm(forms.Form):
    text = forms.CharField(
        max_length=200, label='asd', validators=[validate_file_extension], required=True
    )
