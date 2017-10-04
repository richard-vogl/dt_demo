# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import youtube_dl
import numpy as np

import madmom.audio.signal as sig

from pydub import AudioSegment
from scipy.io.wavfile import write
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.staticfiles.templatetags.staticfiles import static

from .forms import *
from .models import *
from .harmonic_percussive_sep import median_sep


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
)


def index(request):
    # Handle file upload
    if request.method == 'POST':
        if "youtubeform" in request.POST:
            file_input = DocumentForm()
            setting_input = SettingsForm()
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
            setting_input = SettingsForm()
            check = "True"
            if file_input.is_valid():
                new_file = Document(docfile=request.FILES['docfile'])
                new_file.save()
                # so file doesn't get stored in db because we need to delete it anyways
                new_file.delete()

                fid = os.path.basename(new_file.docfile.name)
                fid = os.path.splitext(fid)[0]

                # mp3 to wav and delete mp3 upload
                if '.mp3' in new_file.docfile.name:

                    sound = AudioSegment.from_mp3(settings.DOWNLOAD_DIR+fid+'.mp3')
                    sound.export(settings.DOWNLOAD_DIR+fid+'.wav', format="wav")
                    os.remove(settings.DOWNLOAD_DIR+fid+'.mp3')

                request.session['file_id'] = fid

                # Redirect to loading page
                return HttpResponseRedirect(reverse('loading'))

        if "setting" in request.POST:

            # can't check if valid because Checkbox does not post False value with jquery
            try:
                mode = request.POST.get('setting')
                if mode == settings.CRNN_MODEL \
                        or mode == settings.BRNN_MODEL \
                        or mode == settings.CNN_MODEL:
                    request.session['madmom_mode'] = mode
                else:
                    return JsonResponse({'error_text': 'Seems like you are trying to do something stupid'})
            except TypeError:
                return JsonResponse({'error_text': 'There seems to be a problem with your session'})
            try:
                if "on" in request.POST.get('crnn_checkbox'):
                    request.session['CRNN_mode'] = True
            except TypeError:
                request.session['CRNN_mode'] = False
            return JsonResponse({'error_text': 'None'})

    else:
        # On Page load
        file_input = DocumentForm()
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
        # TODO: error Handling
        try:
            return JsonResponse({'loading_msg': request.session.get('loading_msg'), 'error_text': 'None',
                                'done': request.session.get('done_loading')})
        except TypeError:
            return JsonResponse({'loading_msg': '-', 'error_text': 'None',
                                 'done': True})

    else:
        # TODO: set an interval Parameter in the JSONResponse for the loading msg checks
        request.session['loading_msg'] = "Processing"
        request.session['done_loading'] = False

    return render(
        request,
        'drumtranscription/loading.html',
    )


def player(request):
    return render(
        request,
        'drumtranscription/player.html'
    )


def calculate(request):
    # TODO: ask if handling errors for os.system calls necessary
    if request.method == 'POST':
        # --- add session parameters ----

        request.session['harmonic_postfix'] = '_harm'
        request.session['synthesized_postfix'] = '_synt'
        request.session.save()

        # --- get all parameters ----
        # TODO: handle error message
        try:
            fid = request.session.get('file_id')
            madmom_mode = request.session.get('madmom_mode')
            crnn_mode = request.session.get('CRNN_mode')

            base_dir = settings.BASE_DIR
            file_path = settings.DOWNLOAD_DIR
            crnn_model = settings.CRNN_MODEL

            harm_postfix = request.session.get('harmonic_postfix')
            synt_postfix = request.session.get('synthesized_postfix')

            sound_font_name = '241.SF2'
        except TypeError:
            request.session['done_loading'] = True
            request.session.save()
            return JsonResponse({'error_text': 'None'})

        # ---- process the downloaded audio files with madmom ----
        # download made sure that everything is in .wav format
        # just to be sure maybe loading function does not get called for some reasons
        request.session['loading_msg'] = "Processing"
        request.session.save()
        madmom_file_str = file_path + fid
        madmom_input_file = madmom_file_str + '.wav'
        madmom_output_file = madmom_file_str + '.txt '
        madmom_mode = '-m ' + madmom_mode + ' '
        madmom_rand = ''

        if crnn_model in madmom_mode:
            if crnn_mode:
                madmom_rand = '--rand '

        madmom_command_str = 'DrumTranscriptor ' + \
                             madmom_mode + madmom_rand + \
                             'single -o ' + madmom_output_file + madmom_input_file

        LOGGER.debug('starting madmom processing with command: \n %s\n', madmom_command_str)
        os.system(madmom_command_str)

        # ----  txt to midi ----
        request.session['loading_msg'] = "Synthesizing"
        request.session.save()
        txt2midi_path = base_dir + '/midi2txt/midi2txt/txt_to_midi.py '
        # TODO: maybe add options here
        txt2midi_options = ' -t 100 '
        txt2midi_input_file = '-i ' + madmom_output_file + ' '
        txt2midi_output = file_path + fid + '.midi'
        txt2midi_output_file = '-o ' + txt2midi_output
        txt2midi_command_str = 'python3.5 ' + txt2midi_path + txt2midi_input_file + \
                               txt2midi_output_file + txt2midi_options

        LOGGER.debug('txt to midi conversion with command:\n %s\n', txt2midi_command_str)
        os.system(txt2midi_command_str)

        # ---- harmonic sep ----
        harmonic_output_file = file_path + fid + harm_postfix + '.wav'
        audio, fs = sig.load_audio_file(madmom_input_file, num_channels=1, sample_rate=44100)
        LOGGER.debug('stealing drums from .wav file')
        perc, harm = median_sep(audio, fs)

        scaled = np.int16(harm * 32767)
        write(harmonic_output_file, fs, scaled)

        # ---- midi to wav ----
        request.session['loading_msg'] = "Finalizing"
        request.session.save()

        # TODO: control options
        # TODO: find out why the .wav is shorter than the original and the .mp3 is as long as the original
        timidity_options = '\" -idqq -B2,8 -A100,100a -a -U -s 44100  -D 0-2 -EFchorus=0 -EFreverb=0 -EFx=0 -OwM -o \"'
        timidity_sound_font = base_dir + '/drumtranscription' + static('drumtranscription/'+sound_font_name)
        timidity_output_file = file_path + fid + synt_postfix + '.wav'
        timidity_input_file = txt2midi_output

        LOGGER.debug('midi to wav conversion with command: \n %s\n', txt2midi_command_str)

        timidy_command_str = "timidity -x \"soundfont " + timidity_sound_font + "\" \"" + \
                             timidity_input_file + timidity_options + timidity_output_file + "\""
        os.system(timidy_command_str)

        sound_original = AudioSegment.from_wav(settings.DOWNLOAD_DIR + fid + '.wav')
        sound_harm = AudioSegment.from_wav(settings.DOWNLOAD_DIR + fid + harm_postfix + '.wav')
        sound_synt = AudioSegment.from_wav(settings.DOWNLOAD_DIR + fid + synt_postfix + '.wav')

        sound_original.export(settings.DOWNLOAD_DIR + fid + '.mp3', format='mp3')
        sound_harm.export(settings.DOWNLOAD_DIR + fid + harm_postfix + '.mp3', format='mp3')
        sound_synt.export(settings.DOWNLOAD_DIR + fid + synt_postfix + '.mp3', format='mp3')

        os.remove(settings.DOWNLOAD_DIR + fid + '.wav')
        os.remove(settings.DOWNLOAD_DIR + fid + harm_postfix + '.wav')
        os.remove(settings.DOWNLOAD_DIR + fid + synt_postfix + '.wav')

        # ---- tell loading we are done ----

        request.session['done_loading'] = True
        request.session.save()
    return JsonResponse({'loading_msg': request.session.get('loading_msg'), 'error_text': 'None',
                         'done': True})


def download_youtube(url):
    fid = str(uuid.uuid4())
    path = settings.DOWNLOAD_DIR + fid + '.%(ext)s'

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': path,
        'no-playlist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '256',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return fid


def make_json_error(error_msg):
    error = {'error': True, 'error_msg': error_msg}
    return error
