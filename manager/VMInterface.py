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
