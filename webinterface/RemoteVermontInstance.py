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
from Ft.Xml.Domlette import NonvalidatingReader

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
        self._conn = xmlrpclib.Server(url, allow_none=True)
        self.host = re.match("http://(.*)[:/$]", url).group(1)
        self.running()
        if self.online:
            self.retrieveConfig()


    def running(self):
        try:
            r = self._conn.running()
            self.online = True
            return r
        except e:
            self.online = False
            self.status = str(e) 
            return False
    

    def _retrieveConfig(self):
        self._conn.retrieveConfig()
        return self._conn.cfgText


    def _retrieveSensorData(self):
        self._conn.retrieveSensorData()
        return self._conn.sensorDataText
            
            
    def _transmitConfig(self):
        self._conn.setConfig(self._cfgtext)
        self.cfgModified = False
        self._conn.syncConfig()
        
        
    def _transmitDynConfig(self):
        self._conn.dynCfgText = self.dynCfgText
        self._conn.dynCfgModified = True
        self._conn.syncConfig()
        self.dynCfgModified = False
        
        
    def retrieveLog(self):
        self._conn.retrieveLog()
        self.logText = self._conn.logText
        
        
    def reload(self):
        self._conn.reload()
        
        
    def start(self):
        self._conn.start()
        
        
    def stop(self):
        self._conn.stop()
