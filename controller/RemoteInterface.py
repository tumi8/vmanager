
from LocalVermontInstance import LocalVermontInstance


class RemoteInterface(LocalVermontInstance):
    
    """
    represents external RPC interface to central Vermont Manager Webinterface,
    joins functionality both of LocalVermontInstance and RRDVermontMonitor
    
    @ivar _vMonitor
    """
    
    def __init__(self, dir, cfgfile, logfile, vmonitor):
        LocalVermontInstance.__init__(self, dir, cfgfile, logfile, False)
        self._vMonitor = vmonitor


    def getGraph(self, idx1, idx2):
        return self._vMonitor.get_graph(idx1, idx2)