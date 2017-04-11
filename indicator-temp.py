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

import sys
import logging
import pygame
from gi.repository import Gtk, GLib, AppIndicator3

from status import Status


#logging.basicConfig(file=open("/tmp/indicatorall.log", "w+"),level=logging.INFO)
logging.basicConfig(file = sys.stderr, level = logging.INFO)
pygame.init()
        
class IndicatorTemp:
    def __init__(self):
        self.ind = AppIndicator3.Indicator.new("indicator-temp", "temperature-1-icon", 
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        #self.ind.set_label("0C", "100C")
        self.menu = Gtk.Menu()
        self.temp_mitem = Gtk.MenuItem("0.0 C")
        self.temp_mitem.show()
        self.menu.append(self.temp_mitem)

        item = Gtk.MenuItem("Exit")
        item.connect("activate", self.handle_menu_exit)
        item.show()
        self.menu.append(item)

        self.ind.set_menu(self.menu)
        self.menu.show()

        self.checking_temp = False
        self.check_temp()
        GLib.timeout_add_seconds(2, self.handle_timeout)


    def handle_menu_exit(self):
        logging.info("Exit called")
        Gtk.main_quit()


    def handle_timeout(self):
        self.check_temp()
        return True


    def check_temp(self):
        if self.checking_temp: return True
        self.checking_temp = True
        (temp, temp_str) = Status.getTemp()
        if temp < 60: iconNum = 1
        elif temp < 70: iconNum = 2
        elif temp < 80: iconNum = 3
        elif temp < 90: iconNum = 4
        else: iconNum = 5
        self.ind.set_icon("temperature-%d-icon" % iconNum)
        self.temp_mitem.set_label(temp_str)
        #self.ind.set_label("%.0fC" % temp, "100C")
        self.checking_temp = False
        return True


    def onExit(self, event=None):
        logging.info("Terminated")
        Gtk.main_quit()


def main(args):
    ind = IndicatorTemp()
    try:
        Gtk.main()
    except KeyboardInterrupt:
        ind.onExit()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

