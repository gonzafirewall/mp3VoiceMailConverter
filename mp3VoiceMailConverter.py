#!/usr/bin/python

#############################################################
#
# Autor: Alejandro Ferrari (cdgraff[@]gmail.com)
# Date: 2012-11-16
# Release: 1.0
#
#############################################################

import os
import sys
import pyinotify
from subprocess import call
from config import WATCH_FOLDER
from config import LOG_FILE
import logging
import hashlib


logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s %(message)s')

wm = pyinotify.WatchManager()
mask = pyinotify.IN_MOVED_TO
folder = WATCH_FOLDER

def generate_name(wav_file):
    m = hashlib.md5()
    m.update(open(wav_file).read())
    mp3_name = "msg%s.mp3" % int(m.hexdigest(), base=16)
    return mp3_name

def remove_wavs(wav_name_path):
    for ext in ['.wav', '.WAV']:
        try:
            os.remove(wav_name_path+ext)
        except:
            logging.warning("%s not found" % wav_name_path+ext)

def rename_txt(name, mp3_name):
    ext = '.txt'
    old_txt = name + ext
    new_txt = mp3_name + ext
    os.rename(old_txt, new_txt)

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MOVED_TO(self, event):
        wav_name_path, ext = os.path.splitext(event.pathname)
        basedir = os.path.dirname(event.pathname)
        if ext == '.wav':
            logging.info('Get an Wav file called %s' % event.pathname)
            wav_file = event.pathname
            mp3_name = generate_name(wav_file)
            mp3_file = os.path.join(basedir, mp3_name)
            mp3_name_path = os.path.splitext(mp3_file)[0]
            try:
                logging.info('Converting %s to mp3' % event.pathname)
                retcode = call("/usr/bin/lame" +
                               " --silent -b 16 -m m -q 9 --resample 8 "
                               + wav_file + " " + mp3_file, shell=True)
                if retcode < 0:
                    print >>sys.stderr, "Child was terminated by signal", -retcode
                    logging.info('Child was terminated by signal %s' % retcode)
                else:
                    logging.info('File %s converted succesfully' % event.pathname)
                    os.chown(mp3_file, 100, 101);
                    logging.info('new mp3 file %s' % mp3_file)
                    rename_txt(wav_name_path, mp3_name_path)
                    logging.info('txt rename from %s to %s' % (wav_name_path, mp3_name_path))
                    remove_wavs(wav_name_path)
            except OSError, e:
                logging.info('Execution failed: %s' % e)
                print >>sys.stderr, "Execution failed:", e

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(folder, mask, rec=True)
logging.info('mp3converter init...')
notifier.loop()
