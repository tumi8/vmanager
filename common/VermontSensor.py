

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
    
    def __init__(self, vinstance, id, xpath, threshold, activation):
        self.vinstance = vinstance
        self.id = id
        self.dataXPath = xpath
        self.threshold = int(threshold)
        self.activation = activation
        self.actors = []
    
    
    def check(self):
        """
        @param xml: sensor data as parsed xml object
        """
        v = self.vinstance.sensorDataXml.xpath(self.dataXPath)
        activate = False
        if (self.activation=="positive") and (v>=self.threshold):
            activate = True
        if (self.activation=="negative") and (v<=self.threshold):
            activate = True
        print "sensor id=%s senses value=%s" % (self.id, v)
        for a in self.actors:
            a.trigger(activate)