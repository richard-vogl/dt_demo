# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pkg_resources

from .forms import DocumentForm
from .models import *
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import loader

# Create your views here.


'''def index(request):

    context = {'param': 'test parameter'}

    template = loader.get_template('drumtranscription/index.html')
    return HttpResponse(template.render(context, request))


    # return render(request, 'drumtranscription/index.html', context)
'''
def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('index'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'drumtranscription/index.html',
        {'form': form}
)
