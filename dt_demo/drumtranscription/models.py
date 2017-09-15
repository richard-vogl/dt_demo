# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import os

from django.conf import settings

# Create your models here.
from django.db import models


def update_filename(instance, filename):
    id = str(uuid.uuid4())
    path = settings.DOWNLOAD_DIR
    ext = os.path.splitext(filename)[1]
    format = id + ext
    return os.path.join(path, format)


class Document(models.Model):
    file = models.FileField(upload_to=update_filename)


class Text(models.Model):
    text = models.CharField(max_length=200)
