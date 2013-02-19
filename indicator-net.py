#!/usr/bin/python -u

import sys, time, logging, gtk, appindicator
from status import Status

logging.basicConfig(file = sys.stderr, level = logging.INFO)
gtk.gdk.threads_init()
        

class IndicatorNet:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-net", "", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_icon("idle-network")
        self.ind.set_label(" Init...")
        self.menu = gtk.Menu()
        self.netMenuItem = gtk.MenuItem("network")
        self.menu.add(self.netMenuItem)
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.reading_net = False
        self.statusStr = "init..."
        self.counter = 0
        self.fetch_timer = gtk.timeout_add(1500, self.read_net)
        self.t = time.time()

    def read_net(self, event=None):
        if self.reading_net: return gtk.TRUE
        self.reading_net = True
        inKB, outKB = Status.getNet()
        if inKB > 999: inKB = 999
        if outKB > 999: outKB = 999
        self.statusStr = "%03d" % inKB +":"+"%03d" % outKB +"K/s " + " " + \
            Status.getPingTime("192.168.2.1") + " " + Status.getPingTime("google.com") 
        self.counter += 1
        print "%.2f " % (time.time() - self.t), self.statusStr
        self.ind.set_label(self.statusStr)
        self.netMenuItem.set_label(self.statusStr)
        icon_name = "network"
        net_level = 5.0
        if outKB >= net_level: 
            icon_name += "-transmit"
        if inKB >= net_level:
            icon_name += "-receive"
        if outKB < net_level and inKB < net_level:
            icon_name = "idle-network"
        self.ind.set_icon(icon_name)
        self.t = time.time()
        self.reading_net = False
        return gtk.TRUE

    def onExit(self, event=None):
        logging.info("Terminated")
        try: gtk.main_quit()
        except RuntimeError: pass

def main(args):
    i = IndicatorNet()
    try:
        gtk.main()
    except KeyboardInterrupt:
        i.onExit()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

