# Vermont Management Infrastructure
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
from StringIO import StringIO
from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.Domlette import Print


from VermontLogger import logger



class VermontInstance(object):
    """represents an abstract instance of vermont

    @var __cfgModified: 
    @type __cfgModified: boolean
    @var __dynCfgModified: 
    @var __cfgText: configuration of Vermont as text
    @var __cfgXml: configuration of Vermont as DOM tree, DO NOT MODIFY, only modify text!
    @var __dynCfgText: dynamic configuration of Vermont as text, DO NOT MODIFY, only modify DOM tree!
    @var __dynCfgXml: dynamic configuration of Vermont as DOM tree
    @var __sensorDataText:  
    @var __sensorDataXml: 
    @var __logText:  
    @var __parseXml: True if all XML data should be parsed into a DOM tree
    @var __running: True if vermont is running
    """

    def __init__(self, parsexml):
        self.__cfgModified = False
        self.__dynCfgModified = False
        self.__cfgXml = None
        self.__dynCfgXml = None
        self.__parseXml = parsexml
        self.__logText = ""
        self.__sensorDataText = ""
        self.__sensorDataXml = None
        self.__cfgText = ""
        self.__dynCfgText = ""
        self.__running = False
        
              
    def retrieveConfig(self):
        """
        retrieves original configuration from vermont instance and replaces current configurations,
        both original and dynamic
        """
        logger().debug("VermontInstance.retrieveConfig()")
	try:
		self.setConfig(self._retrieveConfig())
		self.__cfgModified = False
	except:
		logger().error(traceback.format_exc())


    def setConfig(self, text):
        """
        sets new original configuration xml in this instances, recreates dynamic configuration
        """
        logger().debug("VermontInstance.setConfig()")
        self.__cfgModified = True
        self.__cfgText = text
        if self.__parseXml:
            self.__cfgXml = NonvalidatingReader.parseString(text)
        self.__dynCfgModified = True
        self.__dynCfgText = self.cfgText
        if self.__parseXml:
            self.__dynCfgXml = NonvalidatingReader.parseString(self.__cfgText)
        
                
    def retrieveSensorData(self):
        logger().debug("VermontInstance.retrieveSensorData()")
        self.__sensorDataText = self._retrieveSensorData()
        if self.__parseXml:
            self.__sensorDataXml = NonvalidatingReader.parseString(self.__sensorDataText)
                    
            
    def syncConfig(self):
        """
        synchronizes both original and dynamic configuration to vermont instance
        """
        logger().debug("VermontInstance.syncConfig()")
        if self.__cfgModified:
            self._transmitConfig()
            self.__cfgModified = False
        if self.dynCfgModified:            
            if self.__parseXml:
                textio = StringIO()
                Print(self.dynCfgXml, stream=textio)
                self.__dynCfgText = textio.getvalue()
            self._transmitDynConfig()
            self.__dynCfgModified = False
            
            
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
    
    
    def getCfgModified(self):
        return self.__cfgModified


    def getDynCfgModified(self):
        return self.__dynCfgModified


    def getCfgXml(self):
        return self.__cfgXml


    def getDynCfgXml(self):
        return self.__dynCfgXml


    def getLogText(self):
        return self.__logText


    def getSensorDataText(self):
        return self.__sensorDataText


    def getSensorDataXml(self):
        return self.__sensorDataXml


    def getCfgText(self):
        if self.__cfgText == "": self.retrieveConfig()
        return self.__cfgText


    def getDynCfgText(self):
        if self.__cfgText == "": self.retrieveConfig()
        return self.__dynCfgText


    def getRunning(self):
        return self.__running


    def setCfgModified(self, value):
        self.__cfgModified = value


    def setDynCfgModified(self, value):
        self.__dynCfgModified = value


    def setLogText(self, value):
        self.__logText = value


    def setSensorDataText(self, value):
        self.__sensorDataText = value


    def setCfgText(self, value):
        logger().debug("setting new cfgtext")
        self.__cfgText = value


    def setDynCfgText(self, value):
        logger().debug("setting new dyncfgtext")
        self.__dynCfgText = value


    def setRunning(self, value):
        self.__running = value

    cfgModified = property(getCfgModified, setCfgModified, None, None)
    dynCfgModified = property(getDynCfgModified, setDynCfgModified, None, None)
    cfgXml = property(getCfgXml, None, None, None)
    dynCfgXml = property(getDynCfgXml, None, None, None)
    logText = property(getLogText, setLogText, None, None)
    sensorDataText = property(getSensorDataText, setSensorDataText, None, None)
    sensorDataXml = property(getSensorDataXml, None, None, None)
    cfgText = property(getCfgText, setCfgText, None, None)
    dynCfgText = property(getDynCfgText, setDynCfgText, None, None)
    running = property(getRunning, setRunning, None, None)