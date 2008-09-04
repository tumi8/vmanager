
import thread
import time
import traceback
import ConfigParser


from RemoteVermontInstance import RemoteVermontInstance
from VermontConfigurator import VermontConfigurator 


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
    """
    
    def __init__(self, workdir, loadconfig = True):
        self._workDir = workdir
        self._checkInterval = 10
        self.vermontInstances = []
        self._exitWorker = False
        if loadconfig:
            self._readConfig()
            self._configurator = VermontConfigurator()
            self._configurator.parseConfigs(self.vermontInstances)        
        
        
    def _readConfig(self):
        cp = ConfigParser.ConfigParser()
        cp.read(self._workDir+"/vermont_web.conf")
        sec = "Configurator"
        self._checkInterval = cp.getint(sec, "interval")
        
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
              
    
    def startConfigThread(self):
        "starts internal reconfiguration thread"
        self._exitWorker = False
        thread.start_new_thread(VermontInstanceManager.configThreadWorker, (self, ))
        
        
    def stopConfigThread(self):
        "stops internal reconfiguration thread"
        print "initiating reconfiguration thread shutdown"
        self._exitWorker = True
        
        
    def configThreadWorker(self):
        "internal worker thread that regularly checks sensors, actors and parses configuration data"
        print "VermontInstanceManager.configThreadWorker: starting"
        while not self._exitWorker:            
            for vi in self.vermontInstances:                
                try:
                    print "getting sensor data for instance %s" % vi
                    vi.retrieveSensorData()
                except:
                    traceback.print_exc()                    
                
            print "checking sensors"
            self._configurator.checkSensors()
            
            print "saving modified configurations to vermont"
            for vi in self.vermontInstances:
                print vi.dynCfgModified
                if vi.dynCfgModified:                
                    try:                    
                        vi.syncConfig()                        
                    except:
                        print "error occured while saving config for vermont instance %s" % vi
                        traceback.print_exc()
            
            print "sleeping %d seconds" % self._checkInterval
            time.sleep(self._checkInterval)
        