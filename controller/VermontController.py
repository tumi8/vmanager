
import SimpleXMLRPCServer
import sys
import traceback
import os
import ConfigParser
import thread
import time
from Ft.Xml.Domlette import NonvalidatingReader


d = os.path.dirname(sys.argv[0])
sys.path.insert(0, d + 'common')
sys.path.insert(0, d + 'controller')
sys.path.insert(0, d + '../common')

from RemoteInterface import RemoteInterface
from RRDVermontMonitor import RRDVermontMonitor
from VermontLogger import logger
import VermontLogger


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
    @ivar controllerlogfile
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
        self.controllerlogfile = None
        
        try:            
            VermontLogger.init("vcontroller", "", True)
            self._readConfig(configfile)
            VermontLogger.init("vcontroller", self.controllerlogfile, True)
        except:
            print "failed to read configuration file!"
            logger().error(traceback.format_exc())
                
        
    def _readConfig(self, configfile):
        cp = ConfigParser.ConfigParser()
        cp.read(configfile)
        self.dir = cp.get("Global", "VermontDir")
        self.cfgfile = cp.get("Global", "ConfigFile")
        self.controllerlogfile = cp.get("Global", "ControllerLogFile")
        self.logfile = cp.get("Global", "VermontLogFile")
        self.moninterval = int(cp.get("Stats", "Interval"))
        self.allowedIp = cp.get("Global", "AllowedManagerIP")
        logger().info("Using interval %s" % self.moninterval)
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
        self.rInterface = RemoteInterface(self.dir, self.cfgfile, self.logfile, self.vMonitor, self.names)
                
        # RPC server
        self.server = VCRPCServer(("", 8000), allow_none=True, logRequests=False)
        self.server.allow_reuse_address = True
        self.server.allowedIp = self.allowedIp  #IGNORE:W0201
        self.server.register_instance(self.rInterface)        
        
        
    def serve(self):
        thread.start_new_thread(VermontController._workerThread, (self, ))
        self.server.serve_forever()
                

    def _workerThread(self):
        while True:
            logger().info("VermontController._workerThread: collecting monitoring data now")

            self.rInterface.retrieveStatus()
            if self.rInterface.running:
                # try to read in statistics data several times ...
                xml = None
                trycount = 0
                while xml is None:
                    if trycount>=5:
                        raise RuntimeError("Failed to read sensor data!")
                    try:
                        logger().debug("trying to read sensor data ...")
                        self.rInterface.retrieveSensorData()
                        xml = NonvalidatingReader.parseString(self.rInterface.sensorDataText)
                    except:
                        logger().error(traceback.format_exc())
                        logger().info("failed to read sensor data xml, trying again ...")
                        time.sleep(1)
                    trycount += 1
                self.vMonitor.collect_data(xml)
            else:
                logger().info("VermontController._workerThread: skipping stat recording, as instance is not running")
            time.sleep(self.moninterval)




if len(sys.argv)!=2:
    print "usage: python VermontController.py <configfile>"
    sys.exit(1)
    
vc = VermontController(sys.argv[1])
vc.setup()
vc.serve()