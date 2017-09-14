# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models


class Document(models.Model):
    docfile = models.FileField(upload_to='%Y')
