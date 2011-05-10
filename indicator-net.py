#!/usr/bin/python

import sys, time, logging, gtk, appindicator, threading
from status import Status

logging.basicConfig(file = sys.stderr, level = logging.INFO)
gtk.gdk.threads_init()
        
class FetcherThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.mustExit = False

    def run(self):
        statusStr = " Init... "
        while(self.parent.alive.isSet()):
            if self.mustExit: return
            statusStr = Status.getNet() + " " + Status.getPingTime()
            self.parent.updateText(statusStr)
            time.sleep(2)

class IndicatorNet:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-net", "", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_label(" Init...")
        self.menu = gtk.Menu()
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.alive = threading.Event()
        self.alive.set()
        self.fetcherThread = FetcherThread(self)
        self.fetcherThread.start()


    def updateText(self, text):
        self.ind.set_label(text)

    def onExit(self, event=None):
        logging.info("Terminated")
        self.fetcherThread.mustExit = True
        self.alive.clear()
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

