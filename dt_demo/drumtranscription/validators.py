def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.wav', '.mp3']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')
    if value._size > 20971520:
        raise ValidationError(u'Only Files under 20MB supported.')


def validate_text_youtube_expression(value):
    regex = 'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/(?:watch\?v=|embed' \
            '\/)|\.be\/)(?P<video_id>[\W\-\_]*)(&(amp;)?[\W\?=]*)?'
    from django.core.exceptions import ValidationError
    import youtube_dl
    import re
    reg = re.compile(regex)
    if not reg.match(value):
        raise ValidationError(u'Unsupported URL.')
    if "list" in value:
        raise ValidationError(u'No play-lists allowed.')

    with youtube_dl.YoutubeDL() as ydl:
        info = ydl.extract_info(value, download=False)
        duration = info.get('duration')
        if duration > 500:
            raise ValidationError(u'No video over 500s allowed.')
