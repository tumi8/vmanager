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


from VermontLogger import logger

class VermontSensor:
    
    """
    @ivar id:
    @type id: integer
    @ivar dataXPath:
    @type dataXPath: string
    @ivar threshold:
    @type threshold: float
    @ivar activation: either positive or negative
    @type activation: string
    @ivar actors:
    @type actors: list of VermontActor    
    @ivar vinstance: 
    """
    
    def __init__(self, vinstance, idnumber, xpath, threshold, activation):
        self.vinstance = vinstance
        self.id = idnumber
        self.dataXPath = xpath
        self.threshold = int(threshold)
        self.activation = activation
        self.actors = []
    
    
    def check(self):
        """
        @param xml: sensor data as parsed xml object
        """
        # only activate sensor if Vermont instance is running
        if self.vinstance.running:
            v = self.vinstance.sensorDataXml.xpath(self.dataXPath)
            activate = False
            if (self.activation=="positive") and (v>=self.threshold):
                activate = True
            if (self.activation=="negative") and (v<=self.threshold):
                activate = True
            logger().info("sensor id=%s senses value=%s" % (self.id, v))
            for a in self.actors:
                a.trigger(activate)
        else:
            logger().debug("Vermont not running for sensor id=%s" % self.id)
