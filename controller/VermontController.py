
import SimpleXMLRPCServer
import sys
import traceback
import os
import ConfigParser
import thread
import time

d = os.path.dirname(sys.argv[0])
print d
sys.path.insert(0, d + 'common')
sys.path.insert(0, d + 'controller')
sys.path.insert(0, d + '../common')

from RemoteInterface import RemoteInterface
from RRDVermontMonitor import RRDVermontMonitor


class VCRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):

    """
    @ivar allowedIp:
    """

    def verify_request(self, _, client_address):
        return client_address[0]==self.allowedIp



class VermontController:
    
    """
    @ivar dir
    @ivar cfgfile
    @ivar logfile
    @ivar moninterval
    @ivar allowedIp
    @ivar rrdxpaths
    @ivar rrdnames
    @ivar server
    @ivar rInterface
    @ivar vMonitor
    """
    
    def __init__(self, configfile):
        self.dir = None
        self.cfgfile = None
        self.logfile = None
        self.moninterval = None
        self.allowedIp = None
        self.xpaths = []
        self.names = []
        self.server = None
        self.vMonitor = None
        self.rInterface = None
        
        try:
            self._readConfig(configfile)
        except:
            print "failed to read configuration file!"
            traceback.print_exc()
                
        
    def _readConfig(self, configfile):
        cp = ConfigParser.ConfigParser()
        cp.read(configfile)
        self.dir = cp.get("Global", "VermontDir")
        self.cfgfile = cp.get("Global", "ConfigFile")
        self.logfile = cp.get("Global", "LogFile")
        self.moninterval = int(cp.get("Stats", "Interval"))
        self.allowedIp = cp.get("Global", "AllowedManagerIP")
        print "Using interval %s" % self.moninterval
        i = 1
        self.xpaths = []
        self.names = []
        try:
            while True:
                self.xpaths.append(cp.get("Stats", "XPath_%d" % i))
                self.names.append(cp.get("Stats", "Name_%d" % i))
                i += 1
        except: #IGNORE:W0704
            pass
        
        
    def setup(self):
        # internal management classes        
        self.vMonitor = RRDVermontMonitor(self.xpaths, self.names, self.moninterval)
        self.rInterface = RemoteInterface(self.dir, self.cfgfile, self.logfile, self.vMonitor)
                
        # RPC server
        self.server = VCRPCServer(("", 8000))
        self.server.allow_reuse_address = True
        self.server.allowedIp = self.allowedIp  #IGNORE:W0201
        self.server.register_instance(self.rInterface)        
        
        
    def serve(self):
        thread.start_new_thread(VermontController._workerThread, (self, ))
        self.server.serve_forever()
                

    def _workerThread(self):
        while True:
            print "VermontController.background_thread: collecting monitoring data now"

            self.rInterface.retrieveStatus()
            if self.rInterface.running:
                # try to read in statistics data several times ...
                xml = None
                trycount = 0
                while xml is None:
                    if trycount>=5:
                        raise RuntimeError("Failed to read sensor data!")
                    try:
                        self.rInterface.retrieveSensorData()
                    except:
                        traceback.print_exc()
                        print "failed to read sensor data xml, trying again ..."
                        time.sleep(1)
                    trycount += 1
                self.vMonitor.collect_data(self.rInterface.sensorDataXml)
            else:
                print "VermontManager.rrd_thread: skipping stat recording, as instance is not running"
            time.sleep(self.moninterval)




if len(sys.argv)!=2:
    print "usage: python VermontController.py <configfile>"
    sys.exit(1)
    
vc = VermontController(sys.argv[1])
vc.setup()
vc.serve()