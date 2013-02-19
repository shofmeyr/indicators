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

import sys, os, subprocess, time, psutil, logging, gobject, gtk, appindicator, threading, gnomekeyring
import imaplib, re
import pygame, email.parser, feedparser, urllib
from status import Status

#logging.basicConfig(file=open("/tmp/indicatorall.log", "w+"),level=logging.INFO)
logging.basicConfig(file = sys.stderr, level = logging.INFO)
gtk.gdk.threads_init()
pygame.init()
        
class IndicatorTemp:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-temp", "", 
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_label("")
        self.menu = gtk.Menu()
        self.tempMenuItem = gtk.MenuItem("0.0 C")
        self.menu.add(self.tempMenuItem)
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.checking_temp = False
        self.check_temp()
        self.fetch_timer = gtk.timeout_add(2000, self.check_temp)

    def check_temp(self, event=None):
        if self.checking_temp: return gtk.TRUE
        self.checking_temp = True
        (temp, temp_str) = Status.getTemp()
        if temp < 60: iconNum = 1
        elif temp < 70: iconNum = 2
        elif temp < 80: iconNum = 3
        elif temp < 90: iconNum = 4
        else: iconNum = 5
        self.ind.set_icon("temperature-%d-icon" % iconNum)
        self.tempMenuItem.set_label(temp_str)
        self.checking_temp = False
        return gtk.TRUE

    def onExit(self, event=None):
        logging.info("Terminated")
        gtk.main_quit()

def main(args):
    i = IndicatorTemp()
    try:
        gtk.main()
    except KeyboardInterrupt:
        i.onExit()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

