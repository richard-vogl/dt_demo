from django import forms
from .validators import validate_file_extension, validate_text_youtube_expression


# TODO: is it aprpriate to set the html classes/tags here?
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
        help_text='All common youtube Url\'s should \n work even shortened Url\'s like \n http://youtu.be/BL4hgAoEOto '
    )


class SettingsForm(forms.Form):
    setting = forms.ChoiceField(
        choices=(('CRNN_MODEL', 'CRNN-Model'),
                 ('BRNN_MODEL', 'BRNN-Model'),
                 ('CNN_MODEL', 'CNN-Model'),
                 ),
        required=True, widget=forms.Select(attrs={'onchange': "submitSettings();"})
    )
    crnn_checkbox = forms.BooleanField(widget=forms.CheckboxInput(attrs={'onchange': "submitSettings();"}))
