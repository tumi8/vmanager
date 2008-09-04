
import thread
import time
import traceback
import ConfigParser


from VermontInstance import VermontInstance
from VermontConfigurator import VermontConfigurator 


class VermontInstanceManager:
    """Manages multiple Vermont instances
    
    @ivar vermontInstances: 
    @type vermontInstances: list of VermontInstance
    @ivar _configurator: fdsa 
    @type _configurator: VermontConfigurator
    @ivar _checkInterval: how often are sensors and actors checked? (seconds)
    @type _checkInterval: integer
    @ivar _exitWorker
    @type _exitWorker: boolean  
    """
    
    def __init__(self, configparser):
        if configparser is not None:
            self._readConfig(configparser)
            self._configurator = VermontConfigurator()
            self._configurator.parseConfigs(self.vermontInstances, True)        
        
        
    def _readConfig(self):
        cp = ConfigParser.ConfigParser()
        cp.read(workdir+"/vermont_web.conf")
        sec = "Configurator"
        self._checkInterval = cp.getint(sec, "interval")
        
        sec = "VermontInstances"
        self.vermontInstances = []
        i = 1
        try:
            while True:
                instance = VermontInstance(cp.get(sec, "host_%d" % i))
                self.vermontInstances.append(instance)
                i += 1
        except ConfigParser.NoOptionError:
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
        