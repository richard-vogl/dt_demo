def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.wav']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_text_youtube_expression(value):
    regex = 'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/(?:watch\?v=|embed' \
            '\/)|\.be\/)(?P<video_id>[\W\-\_]*)(&(amp;)?[\W\?=]*)?'
    from django.core.exceptions import ValidationError
    import re
    reg = re.compile(regex)
    if not reg.match(value):
        raise ValidationError(u'Unsupported URL.')
