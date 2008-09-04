
import traceback

from LocalVermontInstance import LocalVermontInstance
from VermontLogger import logger


class RemoteInterface(LocalVermontInstance):
    
    """
    represents external RPC interface to central Vermont Manager Webinterface,
    joins functionality both of LocalVermontInstance and RRDVermontMonitor
    
    @ivar _vMonitor
    @ivar _graphNames
    """
    
    def __init__(self, directory, cfgfile, logfile, vmonitor, graphnames):
        LocalVermontInstance.__init__(self, directory, cfgfile, logfile, False)
        self._graphNames = graphnames
        self._vMonitor = vmonitor

    def retrieveConfig(self):
        return LocalVermontInstance.retrieveConfig(self)


    def retrieveSensorData(self):
        return LocalVermontInstance.retrieveSensorData(self)


    def syncConfig(self):
        return LocalVermontInstance.syncConfig(self)


    def reload(self):
        return LocalVermontInstance.reload(self)


    def stop(self):
        try:
            LocalVermontInstance.stop(self)
        except:
            logger().error(traceback.format_exc())
            raise


    def getGraph(self, idx1, idx2):
        return self._vMonitor.get_graph(idx1, idx2)
    
    
    def getGraphList(self):
        return self._graphNames
    
    
    def start(self):
        try:
            LocalVermontInstance.start(self)
        except:
            logger().error(traceback.format_exc())
            raise