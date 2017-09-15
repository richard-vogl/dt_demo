# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pkg_resources

from .forms import *
from .models import *
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import loader

# Create your views here.


def index(request):
    # Handle file upload
    if request.method == 'POST':
        fileinput = DocumentForm(request.POST, request.FILES)
        youtubeinput = YoutubeForm(request.POST)
        if fileinput.is_valid() and youtubeinput.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            # handle uploaded file with madmom


            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('index'))
    else:
        formA = DocumentForm()  # A empty, unbound form
        formB = YoutubeForm()

    # Render list page with the documents and the form
    return render(
        request,
        'drumtranscription/index.html',
        {'form': formB, 'form2': formA}
)
