
import ConfigParser
from VermontInstance import VermontInstance 


class VermontInstanceManager:
	"""Manages multiple Vermont instances
	
	@ivar vermontInstances 
	@type vermontInstances list of VermontInstance
	@ivar _workDir current working directory
	@type string
	"""
	
	def __init__(self, workdir):
		self._workDir = workdir
		self._readConfig(configfile)
		
		
	def _readConfig(self):
		cp = ConfigParser.ConfigParser()
		cp.read(workdir+"/vermont_web.conf")
		sec = "VermontInstances"
		self.vermontInstances = []
		i = 1
		try:
			while True:
				instance = VermontInstance(cp.get(sec, "host_%d" % i))
				self.vermontInstances.append(instance)
				i += 1
		except ConfigParser.NoOptionError:
			pass
		if i==1:
			raise Exception("no valid remote Vermont instance entries in config!")
		
