#!/usr/bin/python

# This monitors all the things I'm interested in:
# - gmailn
# - cpu %
# - mem %
# - network traffic (in/out)
# - cpu temp
# - battery % and time
# - ping time to google and others
# - s&p 500 current value

import sys, os, subprocess, time, psutil, logging, gobject, gtk, appindicator, threading, gnomekeyring, imaplib, re
import pygame, email.parser, feedparser, urllib
from status import Status

#logging.basicConfig(file=open("/tmp/indicatorall.log", "w+"),level=logging.INFO)
logging.basicConfig(file = sys.stderr, level = logging.INFO)
gtk.gdk.threads_init()
pygame.init()
        
class FetcherThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.mustExit = False

    def run(self):
        i = 0
        statusStr = " Init... "
        while(self.parent.alive.isSet()):
            if self.mustExit: return
            # update stats every 2s
            if not (i % 2):
                battTime, battPerc, onBatt = Status.getBattery()
                self.parent.updateText(battTime)
                if battPerc <= 10: perc = 0
                elif battPerc <= 30: perc = 20
                elif battPerc <= 50: perc = 40
                elif battPerc <= 70: perc = 60
                elif battPerc <= 90: perc = 80
                else: perc = 100
                self.parent.updatePercMenuItem("%.0f" % battPerc + "%")
                if onBatt: self.parent.setIcon("gpm-battery-%03d" % perc)
                else: self.parent.setIcon("gpm-battery-%03d-charging" % perc)
            time.sleep(1)
            i += 1

class IndicatorAll:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-batt", "", appindicator.CATEGORY_SYSTEM_SERVICES)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_label(" Init...")
        self.menu = gtk.Menu()
        self.percMenuItem = gtk.MenuItem("100.0")
        self.menu.add(self.percMenuItem)
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.alive = threading.Event()
        self.alive.set()
        self.fetcherThread = FetcherThread(self)
        self.fetcherThread.start()

    def setIcon(self, iconName):
        self.ind.set_icon(iconName)

    def updatePercMenuItem(self, text):
        self.percMenuItem.set_label(text)

    def updateText(self, text):
        self.ind.set_label(text)

    def onExit(self, event=None):
        logging.info("Terminated")
        self.fetcherThread.mustExit = True
        self.alive.clear()
        try: gtk.main_quit()
        except RuntimeError: pass

def main(args):
    i = IndicatorAll()
    try:
        gtk.main()
    except KeyboardInterrupt:
        i.onExit()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

