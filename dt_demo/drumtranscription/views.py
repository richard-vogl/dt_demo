# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pkg_resources
from .models import *
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_datetime
from django.db.models import Count
from django.http import HttpResponse
from django.template import loader

# Create your views here.


def index(request):

    context = {'param': 'test parameter'}

    template = loader.get_template('drumtranscription/index.html')
    return HttpResponse(template.render(context, request))


    # return render(request, 'drumtranscription/index.html', context)
