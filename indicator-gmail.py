#!/usr/bin/python

# if the icons don't show up, get rid of or update the icon cache, eg at 
# /usr/share/icons/ubuntu-mono-dark/icon-theme.cache



# gets gmail from atom feed

import sys, os, time, logging, gtk, appindicator, threading, gnomekeyring, pygame, feedparser, urllib, \
    pynotify, optparse, getpass

optParser = optparse.OptionParser()
optParser.add_option("-u", action = "store", type = "string", dest = "username",
                            default = "", help = "Username for gmail account. Password is found in gnome keyring.")
optParser.add_option("-a", action = "store", type = "string", dest = "account", 
                            default = "https://mail.google.com/mail", help = "Gmail account http address")
optParser.add_option("-i", action = "store", type = "string", dest = "id", 
                            default = "id", help = "A unique id")
optParser.add_option("-s", action = "store", type = "string", dest = "sound", 
                     default = "/usr/share/sounds/ubuntu/stereo/message-new-instant.ogg", help = "sound file")
optParser.add_option("-c", action = "store", type = "string", dest = "color",
                     default = "blue", help = "color for new message icon (red or blue)")
options = optParser.parse_args()[0]
print options

logging.basicConfig(file = sys.stdout, level = logging.INFO)
gtk.gdk.threads_init()
pygame.init()

logging.info("gmail indicator starting for " + options.username + ", account " + options.account + ", id " + \
                 options.id)

class GnomeKeyring():
    def getPasswd(cls, key):
        if not gnomekeyring.is_available(): 
            logging.error("Cannot get passwords for " + key + " from gnome keyring: not available")
            return None
        keys = gnomekeyring.list_item_ids_sync("login")
        for k in keys:
            try:
                item = gnomekeyring.item_get_info_sync("login", k)
                if key in item.get_display_name(): return item.get_secret()
            except Exception as ex:
                logging.info("Need to unlock login keyring: " + ex.message)
                gnomekeyring.unlock_sync("login", getpass.getpass('Password: '))

        logging.error("Cannot get passwords for " + key + " from gnome keyring: not found")
        return None
    getPasswd = classmethod(getPasswd)
    
class Gmail():
    def __init__(self, username, userkey):
        self.username = username
        self.passwd = GnomeKeyring.getPasswd(userkey)
        if self.passwd == None: logging.error("Cannot get password for", username, "from gnome keyring")
        self.unreadCount = 0
        self.msgIds = {}
        self.opener = urllib.FancyURLopener()

    def getHeaders(self):
        headers = []
        unreadCount = 0
        try:
            f = self.opener.open("https://%s:%s@mail.google.com/mail/feed/atom" % (self.username, self.passwd))
            feed = f.read()
            atom = feedparser.parse(feed)
            if len(atom.entries) != self.unreadCount: 
                print atom.feed.title + (": %d" % len(atom.entries)) + " unread messages"
            # we have not yet seen any of the previous msgs
            for key in self.msgIds.keys(): self.msgIds[key] = ""
            for entry in atom.entries:
                author = entry.author.split("(")[0]
                msgId = int(entry.id.split(":")[2])
                headers.append([entry.author + ": " + entry.title, msgId])
                # print headers[-1][0], id
                if not msgId in self.msgIds:
                    # Now pop up the message
                    pynotify.init(self.username)
                    notification = pynotify.Notification(entry.title + " (" + author + ")", 
                                                         entry.summary, "evolution")
                    notification.show()
                    # set to seen
                    self.msgIds[msgId] = "New"
                else: self.msgIds[msgId] = "Old"

            deletedMsgs = {}
            # clear all the messages that were not seen
            for key in self.msgIds.keys(): 
                if self.msgIds[key] == "": del self.msgIds[key]
            
            unreadCount = len(headers)
            while unreadCount > self.unreadCount:
                pygame.mixer.Sound(options.sound).play()
                time.sleep(1)
                self.unreadCount += 1
            self.unreadCount = unreadCount
        except Exception as ex:
            logging.error("Cannot get gmail subjects for " + self.username + ":" + ex.message)
        # returns both the list of headers, and the list of msg ids that remain
        return headers, self.msgIds

class MsgMenuItem(gtk.MenuItem):
    def __init__(self, text, msg, msgId):
        gtk.MenuItem.__init__(self, text)
        self.msg = msg
        self.msgId = msgId

    def getMsgId(self): 
        return self.msgId

    def getMsg(self):
        return self.msg

class IndicatorGmail:
    def __init__(self):
        self.ind = appindicator.Indicator("indicator-gmail-" + options.id, "",
                                          appindicator.CATEGORY_SYSTEM_SERVICES)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_label("")
        self.menu = gtk.Menu()
        self.gmail = Gmail(options.username, "Gmail password for " + options.username)
        self.addToMenu(options.username, options.account + "/#inbox", "0")
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.checking_mail = False
        self.checkMail()
        self.fetch_timer = gtk.timeout_add(20000, self.checkMail)
        
    def checkMail(self, event=None):
        if self.checking_mail: return gtk.TRUE
        self.checking_mail = True
        headers, msgIds = self.gmail.getHeaders()
        hasChanged = False
        # remove messages that are no longer in the list, skipping the first element
        first = True
        for child in self.menu.get_children(): 
            if first: first = False
            elif not child.getMsgId() in msgIds: 
                hasChanged = True
                self.menu.remove(child) 
        # now add all new headers to the menu
        for h in headers: 
            if msgIds[h[1]] == "New": 
                hasChanged = True
                self.addToMenu("       " + h[0], options.account + "/#inbox/%x" % h[1], h[1])
        # set the text on the panel
        num_messages = len(headers)
        if num_messages > 21: num_messages = 21
        self.ind.set_label("%d" % num_messages)
        if len(headers) > 0: 
            if options.color == "red": icon_name = "new-messages-red-%d" % num_messages
            else: icon_name = "indicator-messages-new-%d" % num_messages
            self.ind.set_icon(icon_name)
        else: self.ind.set_icon("indicator-messages") 
        if hasChanged: self.menu.show_all()
        self.checking_mail = False
        return gtk.TRUE

    def onMailActivated(self, event=None):
        os.system("/usr/bin/firefox " + event.getMsg())
        
    def addToMenu(self, text, msg, msgId):
        i = MsgMenuItem(text, msg, msgId)
        i.connect("activate", self.onMailActivated)
        self.menu.add(i)

    def onExit(self, event=None):
        logging.info("Terminated")
        gtk.main_quit()

def main(args):
    i = IndicatorGmail()
    try:
        gtk.main()
    except KeyboardInterrupt:
        i.onExit()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

