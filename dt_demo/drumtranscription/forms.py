from django import forms
from .validators import validate_file_extension, validate_text_youtube_expression


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file', validators=[validate_file_extension], required=True,
        widget=forms.FileInput(attrs={'class': 'inputform'}),
        help_text='Only .wav allowed'
    )


class YoutubeForm(forms.Form):
    text = forms.CharField(
        max_length=200, label='Paste a Youtube Url', validators=[validate_text_youtube_expression],
        required=True, widget=forms.TextInput(attrs={'placeholder': 'Youtube Url', 'class': 'inputform'}),
        help_text = 'All common youtube Url\'s should \n work even shortened Url\'s'
    )


