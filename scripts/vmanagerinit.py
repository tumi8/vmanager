#!/usr/bin/python 
import sys
import os
import xmlrpclib
import ConfigParser


workdir = os.path.dirname(__file__)
sys.path.insert(0, workdir)

cp = ConfigParser.ConfigParser()
cp.read("%s/vermont.conf" % workdir)
sec = "Global"
url = cp.get(sec, "VManager")

remotevm = xmlrpclib.ServerProxy(url, None, None, 1, 1)

def perform_start():
    try:
        remotevm.start("localhost")
    except:
        pass

def perform_stop():
    try:
        remotevm.stop("localhost")
    except:
        pass

def usage():
    print """Usage:
    vmanagerinit.py start
    vmanagerinit.py stop
    """
    sys.exit(1)


if len(sys.argv) == 1:
    usage()

if sys.argv[1] == "start":
    perform_start()
elif sys.argv[1] == "stop":
    perform_stop()
else:
    usage()

