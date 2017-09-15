# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import youtube_dl

from .forms import *
from .models import *

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings


def index(request):
    # Handle file upload
    if request.method == 'POST':
        if "youtubeform" in request.POST:
            file_input = DocumentForm()
            youtube_input = YoutubeForm(request.POST)
            check = "False"
            if youtube_input.is_valid():
                url = youtube_input.cleaned_data.get('text')
                fid = download_youtube(url)

                request.session['file_id'] = fid

                # Redirect to madmom page
                return HttpResponseRedirect(reverse('index'))

        if "fileform" in request.POST:
            file_input = DocumentForm(request.POST, request.FILES)
            youtube_input = YoutubeForm()
            check = "True"
            if file_input.is_valid():
                new_file = Document(docfile=request.FILES['docfile'])
                new_file.save()
                # so file doesn't get stored in db because we need to delete it anyways
                new_file.delete()
                fid = os.path.basename(new_file.docfile.name)
                fid = os.path.splitext(fid)[0]

                request.session['file_id'] = fid

                # Redirect to madmom page
                return HttpResponseRedirect(reverse('index'))

    else:
        print(request.session.get('file_id', '-1'))
        file_input = DocumentForm()  # A empty, unbound form
        youtube_input = YoutubeForm()
        check = "False"

    # Render list page with the documents and the form
    return render(
        request,
        'drumtranscription/index.html',
        {'youtubeform': youtube_input, 'fileform': file_input, 'check': check},
    )


def download_youtube(url):
    fid = str(uuid.uuid4())
    path = settings.DOWNLOAD_DIR + fid + '.%(ext)s'

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '256',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return fid
