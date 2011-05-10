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
        while(self.parent.alive.isSet()):
            if self.mustExit: return
            # update stats every 2s
            temp = Status.getTemp()
            if temp < 50: iconNum = 1
            elif temp < 70: iconNum = 2
            elif temp < 80: iconNum = 3
            elif temp < 90: iconNum = 4
            else: iconNum = 5
            self.parent.setIcon("/home/sah/dev/indicators/temperature-%d-icon.png" % iconNum)
            self.parent.updateTempMenuItem("%.1f C" % temp)
            time.sleep(2)

class IndicatorTemp:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-temp", "/home/sah/dev/indicators/temperature-1-icon.png", 
                                          appindicator.CATEGORY_APPLICATION_STATUS)
                                          
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_label("")
        self.menu = gtk.Menu()
        self.tempMenuItem = gtk.MenuItem("0.0 C")
        self.menu.add(self.tempMenuItem)
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.alive = threading.Event()
        self.alive.set()
        self.fetcherThread = FetcherThread(self)
        self.fetcherThread.start()

    def updateTempMenuItem(self, text):
        self.tempMenuItem.set_label(text)

    def setIcon(self, iconName):
        self.ind.set_icon(iconName)

    def updateText(self, text):
        self.ind.set_label(text)

    def onExit(self, event=None):
        logging.info("Terminated")
        self.fetcherThread.mustExit = True
        self.alive.clear()
        try: gtk.main_quit()
        except RuntimeError: pass

def main(args):
    i = IndicatorTemp()
    try:
        gtk.main()
    except KeyboardInterrupt:
        i.onExit()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

