
import Ft.Xml.cDomlette

class VermontActor:
    """
    @ivar instance: corresponding VermontInstance
    @ivar action:
    @ivar code: python code that should be executed on _trigger
    @ivar _trigger: 
    @ivar delay:
    @ivar id:
    @ivar target: XPath to element that should be modified
    @ivar _onceTriggered: 
    @ivar _delayedTriggerTime:
    """
    
    
    def __init__(self, id, action, code, _trigger, delay, target, instance):
        self.id = id
        self.action = action
        self.code = code
        self._trigger = _trigger
        self.delay = delay
        self.target = target
        self.instance = instance
        self._onceTriggered = False
        self._delayedTriggerTime = None
        
        
    def trigger(self, activate):
        """
        all sensors always trigger the actors, but tell if they were activated
        @param activate: true, if sensor has really activated
        """
        if self._trigger=="once":
            self._handleOnce(activate)
        elif self._trigger=="always":
            self._handleAlways(activate)
        elif self._trigger=="delayed":
            self._handleDelayed(activate)
        elif self._trigger=="once delayed":
            self._handleOnceDelayed(activate)
        
        
    def _handleAlways(self, activate):
        """
        trigger always performs action if sensor is activated
        """ 
        if activate:
            self._performAction()
        
        
    def _handleOnce(self, activate):
        """
        trigger performs action if sensor is activated, but only once
        trigger is reenabled, if sensor is deactivated
        """
        if activate and not self._onceTriggered:
            self._performAction()
            self._onceTriggered = True
        elif not activate and self._onceTriggered:
            self._onceTriggered = False
            
            
    def _handleOnceDelayed(self, activate):
        """
        trigger performs action if sensor is activated for equal or more than self.delay seconds, but only once
        it is reactivated, if sensor is deactivated for equal or more than self.delay seconds
        """
        if activate and self._delayedTriggerTime is None:
            self._delayedTriggerTime = time.time()
            
        elif activate:
            if (time.time()-self._delayedTriggerTime>=self.delay) and not self._onceTriggered:
                self._onceTriggered = True
                self._performAction()
            self._delayedTriggerTime = time.time()
            
        elif not activate and self._onceTriggered:
            if time.time()-self._delayedTriggerTime>=self.delay:
                # enable this _trigger again 
                self._onceTriggered = False
            
            
    def _handleDelayed(self, activate):
        """
        trigger performs action if sensor is activated for equal or more than self.delay seconds, 
        and resets itself afterwards, so that it may be activated after self.delay seconds again
        """
        if activate and self._delayedTriggerTime is None:
            self._delayedTriggerTime = time.time()
        elif activate:
            if time.time()-self._delayedTriggerTime>=self.delay:
                self._delayedTriggerTime = time.time()
                self._performAction()
        elif not activate and self._delayedTriggerTime is not None:
            self._delayedTriggerTime = None
            
            
    def _performAction(self):
        if self.action=="modifyvalue":
            self._performModifyValue()
        elif self.action=="pausemodule":
            pass
        elif self.action=="resumemodule":
            pass
        else:
            raise Exception("unknown action specified for sensor: '%'" % self.action)
        
        
    def _performModifyValue(self):
        nodes = self.instance.dynCfgXml.xpath(self.target)
        if len(nodes)>1:
            print "WARNING: found more than one matching node for xpath string '%s'" % self.target
        targetnode = None
        for n in nodes[0].childNodes:
            if isinstance(n, Ft.Xml.cDomlette.Text):
                targetnode = n
                break
        if targetnode is None:
            raise RuntimeError("failed to find target node for actor with id=%s" % self.id)
        vars = { 'v' : targetnode.nodeValue}
        print "old v: ", vars['v']
        print "code: ", self.code
        try:
            exec self.code in vars
        except:
            print "failed to execute code in instance %s for actor id=%d" % (self.instance, self.id)
            traceback.print_exc()
        print "new v: ", vars['v']
        if vars['v']!=targetnode.nodeValue:
            targetnode.nodeValue = str(vars['v'])
            self.instance.dynCfgModified = True