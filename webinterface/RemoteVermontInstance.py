# Vermont Manager
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


import xmlrpclib
import re

from VermontInstance import VermontInstance
from VermontLogger import logger


class RemoteVermontInstance(VermontInstance):
    "represents a remote instance of vermont"

    url = None
    online = None
    _conn = None
    host = None
    status = None


    def __init__(self, url, parsexml):
        VermontInstance.__init__(self, parsexml)
        self.url = url
        self.online = False
        self._conn = xmlrpclib.ServerProxy(url, None, None, 1, 1)
        self.host = re.match("http://(.*)[:/$]", url).group(1)
        self.retrieveStatus()
        if self.online:
            self.retrieveConfig()
        
        
    def __str__(self):
        return "<remote at host '%s', url '%s'>" % (self.host, self.url)


    def retrieveStatus(self):
        try:
            self._conn.retrieveStatus()
            self.running = self._conn.getRunning()
            self.online = True
            self.status = ["stopped", "running"][self.running]
        except Exception ,e: #IGNORE:W0703
            self.online = False
            self.running = False
            self.status = "error: manager not found on host (%s)" % e
    

    def _retrieveConfig(self):
        self._conn.retrieveConfig()
        return self._conn.getCfgText()


    def _retrieveSensorData(self):
        logger().debug("RemoteVermontInstance._retrieveSensorData()")
        self._conn.retrieveSensorData()
        return self._conn.getSensorDataText()
            
            
    def _transmitConfig(self):
        self._conn.setConfig(self.cfgText)
        self.cfgModified = False
        self._conn.syncConfig()
        
        
    def _transmitDynConfig(self):
        self._conn.setDynCfgText(self.dynCfgText)
        self._conn.setDynCfgModified(True)
        self._conn.syncConfig()
        self.dynCfgModified = False
        
        
    def retrieveLog(self):
        self._conn.retrieveLog()
        self.logText = self._conn.getLogText()
        
        
    def reload(self):
        self._conn.reload()
        
        
    def start(self):
        self._conn.start()
        
        
    def stop(self):
        self._conn.stop()
        
        
    def getGraph(self, idx1, idx2):
        return self._conn.getGraph(idx1, idx2)

    def getGraphList(self):
        return self._conn.getGraphList()