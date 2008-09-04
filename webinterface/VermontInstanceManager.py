
import thread
import time
import traceback
import ConfigParser


from RemoteVermontInstance import RemoteVermontInstance
from VermontConfigurator import VermontConfigurator
from FileLock import FileLock
import VermontLogger
from VermontLogger import logger


class VermontInstanceManager:
    """Manages multiple Vermont instances
    
    @var vermontInstances: 
    @type vermontInstances: list of VermontInstance
    @ivar _configurator: fdsa 
    @type _configurator: VermontConfigurator
    @ivar _checkInterval: how often are sensors and actors checked? (seconds)
    @type _checkInterval: integer
    @ivar _exitWorker
    @type _exitWorker: boolean  
    @ivar _workDir    
    @ivar _logFile
    @ivar _fileLock
    """
    
    def __init__(self, workdir, loadconfig = True):
        self._workDir = workdir
        self._checkInterval = 10
        self.vermontInstances = []
        self._exitWorker = False
        self._logFile = None
        if loadconfig:
            VermontLogger.init("vmanager", "", True)
            self._readConfig()
            self._configurator = VermontConfigurator()
            self._configurator.parseConfigs(self.vermontInstances)
            VermontLogger.init("vmanager", self._logFile, False)
            self._fileLock = FileLock("/tmp/vmanager.lock")
        
        
    def _readConfig(self):
        cp = ConfigParser.ConfigParser()
        cp.read(self._workDir+"/vermont_web.conf")
        sec = "Configurator"
        self._checkInterval = cp.getint(sec, "interval")
        self._logFile = cp.get(sec, "logfile")
        
        sec = "VermontInstances"
        self.vermontInstances = []
        i = 1
        try:
            while True:
                instance = RemoteVermontInstance(cp.get(sec, "host_%d" % i), True)
                self.vermontInstances.append(instance)
                i += 1
        except ConfigParser.NoOptionError: #IGNORE:W0704
            pass
        if i==1:
            raise Exception("no valid remote Vermont instance entries in config!")
        
    
    def reparseVermontConfigs(self):
        self._configurator = VermontConfigurator()
        self._configurator.parseConfigs(self.vermontInstances)
        
    def setup(self):
        if self._fileLock.acquire():
            self._startConfigThread()
              
    
    def _startConfigThread(self):
        "starts internal reconfiguration thread"
        self._exitWorker = False
        thread.start_new_thread(VermontInstanceManager.configThreadWorker, (self, ))
        
        
    def _stopConfigThread(self):
        "stops internal reconfiguration thread"
        logger().info("initiating reconfiguration thread shutdown")
        self._exitWorker = True
        
        
    def configThreadWorker(self):
        "internal worker thread that regularly checks sensors, actors and parses configuration data"
        logger().info("VermontInstanceManager.configThreadWorker: starting")
        try:
            while not self._exitWorker:            
                for vi in self.vermontInstances:                
                    try:
                        vi.retrieveStatus()
                        if vi.running:
                            logger().info("getting sensor data for instance %s" % vi)
                            vi.retrieveSensorData()
                    except:
                        logger().error(traceback.format_exc())                    
                    
                logger().info("checking sensors")
                self._configurator.checkSensors()
                
                logger().info("saving modified configurations to vermont")
                for vi in self.vermontInstances:
                    if vi.dynCfgModified:                
                        try:
                            logger().debug("syncing dynamic config and reloading vermont instance %s" % vi)                    
                            vi.syncConfig()                        
                            vi.reload()
                        except:
                            logger().error("error occured while saving config for vermont instance %s" % vi)
                            logger().error(traceback.format_exc())
                
                logger().info("sleeping %d seconds" % self._checkInterval)
                time.sleep(self._checkInterval)
        except:
            logger().error("error occured in worker thread")
            logger().error(traceback.format_exc())