import traceback

from VermontSensor import VermontSensor
from VermontActor import VermontActor

from VermontLogger import logger

class VermontConfigurator:
    
    """
    @ivar _sensors
    @type _sensors: list of VermontSensor
    """
    
    
    def __init__(self):
        self._sensors = []
    
    
    def parseConfigs(self, vinstances):
        """parses given list of VermontInstances for sensors/actors and recreates internal structure
        @param vinstances:
        @ptype vinstances: array of VermontInstance
        """
        logger().info("VermontConfigurator.parseConfigs: reparsing configuration for sensors and actors")
        self._sensors = []
        for v in vinstances:
            if v.cfgXml is None:
                try:
                    v.retrieveConfig()
                except:
                    logger().error(traceback.format_exc())
            if v.cfgXml is not None:
                try:
                    self._parseSensors(v.cfgXml, v)
                except:
                    logger().warning("failed to parse configuration from instance %s" % v)
                    logger().error(traceback.format_exc())
            else:
                logger().debug("failed to get configuration for vermont instance %s" % v)
        for v in vinstances:
            if v.cfgXml is not None:
                try:
                    self._parseActors(v.cfgXml, v)
                except:
                    logger().warning("failed to parse configuration from instance %s" % v)
                    logger().error(traceback.format_exc())
                
                
    def _parseSensors(self, xml, vinstance):
        logger().debug("VermontConfigurator._parseSensors: called")
        sensors = xml.xpath("/ipfixConfig/sensors/sensor")
        for s in sensors:
            idnumber = s.xpath("string(@id)")
            xpath = s.xpath("string(source)")
            if xpath=="":
                raise RuntimeError("failed to parse source for sensor with id=%s" % idnumber)
            threshold = s.xpath("string(threshold)")
            activation = s.xpath("string(activation)")
            if (activation!="positive") and (activation!="negative"):
                raise RuntimeError("failed to parse element activation")
            for cs in self._sensors:
                if cs.id==idnumber:
                    raise RuntimeError("two sensor ids occured in configuration (id=%s)!" % idnumber)
            logger().debug("VermontConfigurator._parseSensors: found new sensor with id=%s" % idnumber)
            self._sensors.append(VermontSensor(vinstance, idnumber, xpath, threshold, activation))
            
            
    def _parseActors(self, xml, vinstance):
        logger().debug("VermontConfigurator._parseActors: called")
        actors = xml.xpath("/ipfixConfig/actors/actor")
        for a in actors:
            idnumber = a.xpath("string(@id)")
            action = a.xpath("string(action)")
            code = a.xpath("string(code)")
            trigger = a.xpath("string(trigger)")
            delay = a.xpath("string(delay)")
            target = a.xpath("string(target)")
            foundit = False
            for s in self._sensors:
                if s.id==idnumber:
                    foundit = True
                    logger().debug("VermontConfigurator._parseActors: found new actor with id=%s" % idnumber)
                    s.actors.append(VermontActor(idnumber, action, code, trigger, delay, target, vinstance))
            if not foundit:
                raise RuntimeError("failed to find sensor for actor with id=%s" % idnumber)
            
            
    def checkSensors(self):
        """
        checks if any sensors are activated and automatically triggers assigned actors
        -> dynCfg of vermont instances may be modified!
        """
        for s in self._sensors:
            s.check()
    