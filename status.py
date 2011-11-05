#!/usr/bin/python

import sys, os, subprocess, time, psutil, logging, gobject, gtk, appindicator, threading, gnomekeyring, imaplib, re
import pygame, email.parser, feedparser, urllib

class Status():
    pingRe = re.compile("rtt min/avg/max/mdev = (\d+.\d+)")
    netRe = re.compile(r"\s*\S+:\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+")
    tempRe = re.compile("Physical id 0:\s+\+(\d+.\d+)")
    inb = 0
    outb = 0
    lastTime = time.time()

    def getCpuPerc(cls):
        return "%03d" % int(psutil.cpu_percent()) + "%"
    getCpuPerc = classmethod(getCpuPerc)

    def getMemPerc(cls):
        return "%03d" % int(100.0 * (1.0 - float(psutil.avail_virtmem()) / float(psutil.total_virtmem()))) + "m% "
    getMemPerc = classmethod(getMemPerc)

    def getPingTime(cls):
        pingStr = subprocess.Popen("ping -c 1 google.com 2>/dev/null |grep rtt",
                                      stdout=subprocess.PIPE, shell=True).communicate()[0].strip()
        pingMs = -1
        if len(pingStr) > 0: 
            m = Status.pingRe.match(pingStr)
            if m != None: pingMs = min(round(float(m.group(1))), 999)
        return "%03dms" % pingMs
    getPingTime = classmethod(getPingTime)

    def getTemp(cls):
        tempStr = subprocess.Popen("sensors", 
                                   stdout=subprocess.PIPE, shell=True).communicate()[0].strip()
        temp = -1
        if len(tempStr) > 0:
            m = Status.tempRe.match(tempStr)
            if m != None: temp = float(m.group(1))
        return (temp, tempStr)
    getTemp = classmethod(getTemp)

    def getBattery(cls):
        onBatt = False
        perc = 0
        f = open("/proc/acpi/battery/BAT0/state", "r")
        rate = 0
        outstr = "00:00"
        for line in f.readlines():
            tokens = line.split()
            try:
                if tokens[0] == "charging" and tokens[2] == "discharging": onBatt = True
                elif tokens[0] == "present" and tokens[1] == "rate:": rate = float(tokens[2])
                elif tokens[0] == "remaining": remaining = float(tokens[2])
            except ValueError: 
                pass
        f.close()
        if rate != 0:  
            f = open("/proc/acpi/battery/BAT0/info", "r")
            for line in f.readlines():
                tokens = line.split()
                if tokens[0] == "last": 
                    capacity = float(tokens[3])
                    break
            f.close()
            if remaining > capacity: remaining = capacity
            hrs = int(remaining / rate)
            mins = (remaining / rate - hrs) * 60.0
            if hrs > 9: 
                hrs = 0
                mins = 0
            perc = 100.0 * remaining / capacity
            outstr = "%02d:%02d" % (hrs, mins)
        return (outstr, perc, onBatt)
    getBattery = classmethod(getBattery)

    def getNet(cls):
        f = open("/proc/net/dev")
        f.readline()  
        f.readline()
        inb = Status.inb
        outb = Status.outb
        Status.inb = 0.0
        Status.outb = 0.0
        for line in f:
            m = Status.netRe.match(line)
            Status.inb += int(m.group(1))
            Status.outb += int(m.group(2))
        f.close()
        newTime = time.time()
        timeDiff =  newTime - Status.lastTime
        Status.lastTime = newTime
        indiff = (Status.inb - inb) / timeDiff
        outdiff = (Status.outb - outb) / timeDiff
        return "%03d" % (indiff/1024) +":"+"%03d" % (outdiff/1024) +"K/s"
    getNet = classmethod(getNet)


