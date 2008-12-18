# Vermont Management
# Copyright (C) 2008 University of Erlangen, Staff of Informatik 7 <limmer@cs.fau.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import thread
import time
import traceback
import ConfigParser
import SimpleXMLRPCServer
import subprocess


from RemoteVermontInstance import RemoteVermontInstance
from VermontConfigurator import VermontConfigurator
import VermontLogger
from VermontLogger import logger
from VMInterface import VMInterface


class VMRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    """
    @ivar allowedIp:
    """

    def verify_request(self, _, client_address):
        return client_address[0]==self.allowedIp
    

class VermontInstanceManager(VMInterface, object):
    """Manages multiple Vermont instances
    
    @var vermontInstances: 
    @type vermontInstances: list of VermontInstance
    @ivar _configurator: fdsa 
    @type _configurator: VermontConfigurator
    @ivar _checkInterval: how often are sensors and actors checked? (seconds)
    @type _checkInterval: integer
    @ivar _workerRunning 
    @ivar _logFile
    @ivar _allowedIP
    @ivar _server
    @ivar __dynconfEnabled
    @ivar _bindAddress
    @ivar _listenPort
    """
    
    def __init__(self, cfgfile):
        self._checkInterval = 10
        self.vermontInstances = []
        self._exitWorker = False
        self._logFile = None
        self._server = None
        self._allowedIP = ""
        self.__dynconfEnabled = True
        self._workerRunning = False
        if cfgfile is not None:
            VermontLogger.init("vmanager", "", True)
            self._readConfig(cfgfile)
            self._configurator = VermontConfigurator()
            self._configurator.parseConfigs(self.vermontInstances)
            VermontLogger.init("vmanager", self._logFile, True)
        
        
    def _readConfig(self, cfgfile):
        cp = ConfigParser.ConfigParser()
        cp.read(cfgfile)
        sec = "Global"
        self._checkInterval = cp.getint(sec, "Interval")
        self._logFile = cp.get(sec, "Logfile")
        self._allowedIP = cp.get(sec, "AllowedWebIP")
        self._bindAddress = cp.get(sec, "BindAddress")
        self._listenPort = cp.get(sec, "ListenPort")
        
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
        logger().debug("VermontInstanceManager.setup()")
        self._startConfigThread()
        # RPC server
        self._server = VMRPCServer((self._bindAddress, self._listenPort), allow_none=True, logRequests=False)
        self._server.allow_reuse_address = True
        self._server.allowedIp = self._allowedIP # IGNORE:W0201
        self._server.register_instance(self)        
        
        
    def serve(self):
        self._server.serve_forever()
              
    
    def _startConfigThread(self):
        "starts internal reconfiguration thread"
        logger().debug("VermontInstanceManager._startConfigThread()")
        self._workerRunning = True
        thread.start_new_thread(VermontInstanceManager.configThreadWorker, (self, ))
    
        
    def configThreadWorker(self):
        "internal worker thread that regularly checks sensors, actors and parses configuration data"
        logger().info("VermontInstanceManager.configThreadWorker: starting")
        while self.__dynconfEnabled:
            try:            
                for vi in self.vermontInstances:                
                    try:
                        vi.retrieveStatus()
                        if vi.running:
                            logger().debug("getting sensor data for instance %s" % vi)
                            vi.retrieveSensorData()
                    except:
                        logger().error(traceback.format_exc())                    
                    
                logger().debug("checking sensors")
                self._configurator.checkSensors()
                
                logger().debug("saving modified configurations to vermont")
                for vi in self.vermontInstances:
                    if vi.dynCfgModified:                
                        try:
                            logger().debug("syncing dynamic config and reloading vermont instance %s" % vi)                    
                            vi.syncConfig()                        
                            vi.reload()
                        except:
                            logger().error("error occured while saving config for vermont instance %s" % vi)
                            logger().error(traceback.format_exc())
                
                logger().debug("sleeping %d seconds" % self._checkInterval)                
            except:
                logger().error("error occured in worker thread")
                logger().error(traceback.format_exc())
            time.sleep(self._checkInterval)
        self._workerRunning = False
        logger().info("VermontInstanceManager.configThreadWorker: stopping")
            
            
    def _getInstanceByName(self, host):
        for vi in self.vermontInstances:
            if vi.host==host:
                return vi
        raise "host not found"
            
    def getHosts(self):
        h = []
        for vi in self.vermontInstances:
            h.append(vi.host)
        return h
    
    def getStati(self):
        s = []
        for vi in self.vermontInstances:
            vi.retrieveStatus()
            s.append(vi.status)
        return s
    
    def start(self, host):
        self._getInstanceByName(host).start()
        
    def stop(self, host):
        self._getInstanceByName(host).stop()
        
    def reload(self, host):
        self._getInstanceByName(host).reload()
        
    def getConfigs(self, host):
        vi = self._getInstanceByName(host)
        return (vi.getCfgText(), vi.getDynCfgText())
    
    def setConfig(self, host, configtext):
        vi = self._getInstanceByName(host)
        vi.setConfig(configtext)
        vi.syncConfig()
        
    def getSensorData(self, host):
        vi = self._getInstanceByName(host)
        vi.retrieveSensorData()
        return vi.sensorDataText
    
    def getGraphList(self, host):
        vi = self._getInstanceByName(host)
        return vi.getGraphList()
    
    def getGraph(self, host, idx1, idx2):
        vi = self._getInstanceByName(host)
        return vi.getGraph(idx1, idx2)
    
    def getLog(self, host):
        vi = self._getInstanceByName(host)
        vi.retrieveLog()
        return vi.logText

    def getDynconfEnabled(self):
        return self.__dynconfEnabled

    def setDynconfEnabled(self, value):
        self.__dynconfEnabled = value
        if value and not self._workerRunning:
            self._startConfigThread()        
            
    def getManagerLog(self):
        pipe = subprocess.Popen("tail -n 200 %s" % self._logFile, shell=True, bufsize=100*1024, stdout=subprocess.PIPE).stdout
        return "".join(pipe.readlines())

    dynconfEnabled = property(getDynconfEnabled, setDynconfEnabled, None, "DynconfEnabled's Docstring")
