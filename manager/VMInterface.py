


class VMInterface:
    
    def getHosts(self):
        """returns Vermont hosts as list of strings"""
        raise "not implemented"
    
    def start(self, host):
        raise "not implemented"
    
    def stop(self, host):
        raise "not implemented"
    
    def reload(self, host):
        raise "not implemented"
    
    def getConfigs(self, host):
        """returns list with (config, dynconfig) strings as content"""
        raise "not implemented"
    
    def setConfig(self, host, configtext):
        raise "not implemented"
    
    def getSensorData(self, host):
        raise "not implemented"
    
    def getGraphList(self, host):
        raise "not implemented"
    
    def getGraph(self, host, idx1, idx2):
        raise "not implemented"
    
    def getStati(self):
        """
        @return list of status strings, which are prefixed with 'error' when they are not online
        """
        raise "not implemented"
    
    def reparseVermontConfigs(self):
        raise "not implemented"
    
    def getLog(self, host):
        raise "not implemented"
    
    def getDynconfEnabled(self):
        raise "not implemented"
    
    def setDynconfEnabled(self, val):
        raise "not implemented"
    
    def getManagerLog(self):
        raise "not implemented"