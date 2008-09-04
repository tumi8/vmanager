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


    def __init__(self, url):
        VermontInstance.__init__()
        self.url = url
        self.online = False
        self._conn = xmlrpclib.Server(url, allow_none=True)
        self.host = re.match("http://(.*)[:/$]", url).group(1)
        self.checkOnline()
        if self.online:
            self.getConfig()


    def checkOnline(self):
        try:
            self.online = self._conn.is_instance_running()
        except e:
            self.online = false
            self.status = str(e) 
    

    def _retrieveConfig(self):
        self._conn.get_config()


    def _retrieveSensorData(self):
        if self.online:
            return self._conn.get_stats()
        else:
            return ""
            
            
    def _transmitConfig(self):
        self._conn.save_config(self._cfgtext)
        self._cfgModified = False
        
        
    def reload(self):
        self._conn.reload()
