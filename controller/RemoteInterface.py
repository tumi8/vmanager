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
