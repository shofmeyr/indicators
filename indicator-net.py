#!/usr/bin/python -u

import sys, time, logging, gtk, appindicator, socket, struct
from status import Status

logging.basicConfig(file = sys.stderr, level = logging.INFO)
gtk.gdk.threads_init()

def strike(text):
    return ''.join([u'\u0336{}'.format(c) for c in text])[1:]
    
def get_gw():
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

class IndicatorNet:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-net", "", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_icon("network-idle")
        self.ind.set_label(strike("NET "))
        self.menu = gtk.Menu()
        self.netMenuItem = gtk.MenuItem("network")
        self.menu.add(self.netMenuItem)
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.reading_net = False
        self.statusStr = strike("NET ")
        self.counter = 0
        self.fetch_timer = gtk.timeout_add(1500, self.read_net)
        self.t = time.time()
        self.gw = get_gw()
        print "gateway:", self.gw

    def read_net(self, event=None):
        if self.reading_net: return gtk.TRUE
        self.reading_net = True
        inKB, outKB = Status.getNet()
        if inKB > 9999: inKB = 999
        if outKB > 999: outKB = 999
        pingTimeGoogle = Status.getPingTime("google.com")
        
        if self.gw == None:
            self.gw = get_gw()
            print "gateway:", self.gw
        if self.gw != None:
            pingTimeGW = Status.getPingTime(self.gw, 2)
            self.statusStr = "%04d" % inKB +":"+"%03d" % outKB +"K/s " + " " + \
                             pingTimeGoogle + "|" + pingTimeGW + "ms"
            if pingTimeGW == "-1":
                try:
                    self.gw = get_gw()
                    print "gateway:", self.gw
                except:
                    pass
            self.statusStr = self.statusStr
        else:
            self.statusStr = strike("NET ")
        print "%.2f " % (time.time() - self.t), self.statusStr
        self.ind.set_label(self.statusStr)
        if self.gw != None:
            fullStatusStr = "UP: %03d" % inKB +"K/s\n"+"DOWN: %03d" % outKB +"K/s\n" + \
                            "Google ping: " + pingTimeGoogle + "ms\n" + \
                            "GW (" + self.gw + ") ping: " + pingTimeGW
        else:
            fullStatusStr = "No network"
        self.netMenuItem.set_label(fullStatusStr)
        self.counter += 1
        icon_name = "network"
        net_level = 5.0
        if outKB >= net_level: 
            icon_name += "-transmit"
        if inKB >= net_level:
            icon_name += "-receive"
        if outKB < net_level and inKB < net_level:
            icon_name += "-idle"
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

