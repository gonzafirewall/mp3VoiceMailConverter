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

wm = pyinotify.WatchManager()
mask = pyinotify.IN_MOVED_TO
folder = "/var/spool/asterisk/voicemail/default"

class EventHandler(pyinotify.ProcessEvent):

    def process_IN_MOVED_TO(self, event):
	fileName, fileExtension = os.path.splitext(event.pathname)
	if fileExtension == '.wav':
		fileNameWav = fileName + fileExtension
		fileNameMp3 = fileName + ".mp3"
		try:
		    retcode = call("/usr/bin/lame" + " --silent -b 16 -m m -q 9 --resample 8 " + fileNameWav + " " + fileNameMp3, shell=True)
		    if retcode < 0:
		        print >>sys.stderr, "Child was terminated by signal", -retcode
		    else:
		        os.chown(fileNameMp3, 100, 101);
		except OSError, e:
			print >>sys.stderr, "Execution failed:", e

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(folder, mask, rec=True)

notifier.loop()
