import sys

from VermontInstanceManager import VermontInstanceManager



if len(sys.argv)!=2:
    print "usage: python VermontManager.py <configfile>"
    sys.exit(1)

vimanager = VermontInstanceManager(sys.argv[1])
vimanager.setup()
vimanager.serve()