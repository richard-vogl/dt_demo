# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import youtube_dl
import bin
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader

from .forms import *
from .models import *

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

# TODO: check if session fields are set before accessing
def index(request):
    # Handle file upload
    if request.method == 'POST':
        print(request.POST)
        if "youtubeform" in request.POST:
            file_input = DocumentForm()
            youtube_input = YoutubeForm(request.POST)
            check = "False"
            if youtube_input.is_valid():
                url = youtube_input.cleaned_data.get('text')
                fid = download_youtube(url)

                request.session['file_id'] = fid

                # Redirect to loading page
                return HttpResponseRedirect(reverse('loading'))

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

                # Redirect to loading page
                return HttpResponseRedirect(reverse('loading'))

        if "setting" in request.POST:

            # can't check if valid because Checkbox does not post False value with
            request.session['madmom_mode'] = request.POST.get('setting')
            try:
                if "on" in request.POST.get('crnn_checkbox'):
                    request.session['CRNN_mode'] = True
            except TypeError:
                request.session['CRNN_mode'] = False
            # TODO: Error Handling
            return JsonResponse({'error_text': 'None'})

    else:
        # On Page load
        file_input = DocumentForm()  # A empty, unbound form
        youtube_input = YoutubeForm()
        setting_input = SettingsForm()
        check = "False"

    # Render list page with the documents and the form
    return render(
        request,
        'drumtranscription/index.html',
        {'youtubeform': youtube_input, 'fileform': file_input, 'check': check, 'settingform': setting_input},
    )


def loading(request):
    if request.method == 'POST':
        #TODO: check if these session params exist
        return JsonResponse({'loading_msg': request.session.get('loading_msg'), 'error_text': 'None',
                             'done': request.session.get('done_loading')})
    else:
        # TODO: set an interval Parameter in the JSONResponse for the loading msg checks
        request.session['loading_msg'] = "Processing"
        request.session['done_loading'] = False

    return render(
        request,
        'drumtranscription/loading.html',
    )


def calculate(request):
    if request.method == 'POST':
        # TODO: handle error message
        # TODO: add madmom calculation, syntesize midi, look if Finalizing is nessacery
        time.sleep(3)
        request.session['loading_msg'] = "Synthesizing midi"
        request.session.save()
        time.sleep(3)
        request.session['loading_msg'] = "Finalizing"
        request.session.save()
        time.sleep(3)
        request.session['done_loading'] = True
    return HttpResponse("OK")


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
