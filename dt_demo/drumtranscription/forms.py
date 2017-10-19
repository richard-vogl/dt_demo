from django import forms

from django.conf import settings
from .validators import validate_file_extension, validate_text_youtube_expression


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file', validators=[validate_file_extension], required=True,
        widget=forms.FileInput(attrs={'class': 'inputform'}),
        help_text='Only .wav and .mp3 allowed'
    )
    id = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'id':'session_id_1'}))


class YoutubeForm(forms.Form):
    text = forms.CharField(
        max_length=200, label='Paste a Youtube Url', validators=[validate_text_youtube_expression],
        required=True, widget=forms.TextInput(attrs={'placeholder': 'Youtube Url', 'class': 'inputform'}),
        help_text='All common youtube Url\'s should \n work even shortened Url\'s like \n http://youtu.be/BL4hgAoEOto '
    )
    id = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'id': 'session_id_2'}))


class SettingsForm(forms.Form):
    setting = forms.ChoiceField(
        label='Select a Model:',
        choices=((settings.CRNN_MODEL, 'CRNN-Model'),
                 (settings.BRNN_MODEL, 'BRNN-Model'),
                 (settings.CNN_MODEL, 'CNN-Model'),
                 ),
        required=True, widget=forms.Select(attrs={'onchange': "submitSettings();"})
    )
    crnn_checkbox = forms.BooleanField(label='rand:', widget=forms.CheckboxInput(attrs={'onchange': "submitSettings();"}))
    id = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'id': 'session_id_3'}))
