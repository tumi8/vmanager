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


from StringIO import StringIO
from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.Domlette import Print

class VermontInstance:
    """represents an abstract instance of vermont

    @var cfgModified: 
    @type cfgModified: boolean
    @var dynCfgModified: 
    @var cfgText: configuration of Vermont as text
    @var cfgXml: configuration of Vermont as DOM tree, DO NOT MODIFY, only modify text!
    @var dynCfgText: dynamic configuration of Vermont as text, DO NOT MODIFY, only modify DOM tree!
    @var dynCfgXml: dynamic configuration of Vermont as DOM tree
    @var sensorDataText:  
    @var sensorDataXml: 
    @var logText:  
    @var parseXml: True if all XML data should be parsed into a DOM tree
    @var running: True if vermont is running
    """


    def __init__(self, parsexml):
        self.cfgModified = False
        self.dynCfgModified = False
        self.cfgXml = None
        self.dynCfgXml = None
        self.parseXml = parsexml
        self.logText = ""
        self.sensorDataText = ""
        self.sensorDataXml = None
        self.cfgText = ""
        self.dynCfgText = ""
        self.running = False
        
              
    def retrieveConfig(self):
        """
        retrieves original configuration from vermont instance and replaces current configurations,
        both original and dynamic
        """
        self.setConfig(self._retrieveConfig())
        self.cfgModified = False


    def setConfig(self, text):
        """
        sets new original configuration xml in this instances, recreates dynamic configuration
        """
        self.cfgModified = True
        self.cfgText = text
        if self.parseXml:
            self.cfgXml = NonvalidatingReader.parseString(text)
        self.dynCfgText = self.cfgText
        if self.parseXml:
            self.dynCfgXml = NonvalidatingReader.parseString(self.cfgText)
        
                
    def retrieveSensorData(self):
        self.sensorDataText = self._retrieveSensorData()
        if self.parseXml:
            self.sensorDataXml = NonvalidatingReader.parseString(self.sensorDataText)
                    
            
    def syncConfig(self):
        """
        synchronizes both original and dynamic configuration to vermont instance
        """
        print "syncConfig"
        if self.cfgModified:
            self._transmitConfig()
            self.cfgModified = False
        if self.dynCfgModified:            
            if self.parseXml:
                textio = StringIO()
                Print(self.dynCfgXml, stream=textio)
                self.dynCfgText = textio.getvalue()
            self._transmitDynConfig()
            self.dynCfgModified = False
            
            
    def retrieveStatus(self):
        raise "not implemented"
            
    
    def retrieveLog(self):
        raise "not implemented"

    
    def reload(self):
        raise "not implemented"
    
    def start(self):
        raise "not implemented"
    
    def stop(self):
        """
        @return: True if Vermont was successfully stopped, False if not
        """
        raise "not implemented"
    
    def _retrieveConfig(self):
        raise "not implemented"
    
    def _retrieveSensorData(self):
        raise "not implemented"
        return "" # IGNORE:W0101
    
    def _transmitConfig(self):
        raise "not implemented"
    
    def _transmitDynConfig(self):
        raise "not implemented"