#!/usr/bin/python


import SimpleXMLRPCServer
import os
import re
import sys
import ConfigParser
import traceback
import time
import thread
from Ft.Xml.Domlette import NonvalidatingReader
import base64

class RRDVermontMonitor:

	xpaths = None
	names = None
	interval = None
	# record every 10  60  3600 seconds a value in rrd (multiplied by "step" size -s)
	rrdintervals = (2, 12, 720)
	rrdgraphhist = (120, 1440, 10080)

	def __init__(self, xpaths, names, interval):
		self.xpaths = xpaths
		self.names = names
		self.interval = interval

	def collect_data(self, xml):
		if not os.access("rrd", os.R_OK|os.W_OK):
			os.mkdir("rrd")
		rrdfn = "rrd/db_%d_%d.rrd"
		for i in range(0, len(self.xpaths)):
			data = xml.xpath(self.xpaths[i])
			print "inserting value %s for element '%s' (%s)" % (data, self.names[i], self.xpaths[i])
			for j in range(0, len(self.rrdintervals)):
				if not os.access(rrdfn % (i, j), os.R_OK|os.W_OK):
					os.system("rrdtool create %s -s 5 DS:s:GAUGE:%d:U:U RRA:AVERAGE:0.5:%d:10000 RRA:MIN:0.5:%d:10000 RRA:MAX:0.5:%d:10000" % (rrdfn % (i, j), self.rrdintervals[j]*5*2, self.rrdintervals[j], self.rrdintervals[j], self.rrdintervals[j]))
				os.system("rrdtool update %s N:%f " % (rrdfn % (i, j), data))
		pass
	

	def get_graph(self, idx1, idx2):
		rrdfn = "rrd/db_%d_%d.rrd" % (idx1, idx2)
		pngfn = "rrd/db_%d_%d.png" % (idx1, idx2)
		os.system("rrdtool graph %s --imgformat PNG --end now --start end-%dm DEF:ds0b=%s:s:MAX LINE1:ds0b#9999FF:\"min/max\" DEF:ds0c=%s:s:MIN LINE1:ds0c#9999FF DEF:ds0a=%s:s:AVERAGE LINE2:ds0a#0000FF:\"average\"" % (pngfn, self.rrdgraphhist[idx2], rrdfn, rrdfn, rrdfn))
		pic = open(pngfn).read()
		return base64.b64encode(pic)
		

class VermontManager:

	dir = None
	cfgfile = None
	logfile = None
	rrdmonitor = None
	moninterval = None
	allowedIp = None

	def __init__(self):
		if len(sys.argv)<2:
			print "usage: python vermont_manager.py <configfile>"
			sys.exit(1)
		cp = ConfigParser.ConfigParser()
		cp.read(sys.argv[1])
		self.dir = cp.get("Global", "VermontDir")
		self.cfgfile = cp.get("Global", "ConfigFile")
		self.logfile = cp.get("Global", "LogFile")
		self.moninterval = int(cp.get("Stats", "Interval"))
		self.allowedIp = cp.get("Global", "AllowedManagerIP")
		print "Using interval %s" % self.moninterval
		i = 1
		xpaths = []
		names = []
		try:
			while True:
				xpaths.append(cp.get("Stats", "XPath_%d" % i))
				names.append(cp.get("Stats", "Name_%d" % i))
				i += 1
		except:
			pass
		self.rrdmonitor = RRDVermontMonitor(xpaths, names, self.moninterval)


	def rrd_thread(self):
		while True:
			print "VermontManager.background_thread: collecting monitoring data now"

			if self.is_instance_running():
				# try to read in statistics data several times ...
				xml = None
				trycount = 0
				while xml is None:
					if trycount>=5:
						raise Exception("Failed to read statistics data!")
					try:
						text = self.get_stats()
						xml = NonvalidatingReader.parseString(text)
					except:
						traceback.print_exc()
						print "failed to read statistics data xml, trying again ..."
						time.sleep(1)
						pass
					trycount += 1
				self.rrdmonitor.collect_data(xml)
			else:
				print "VermontManager.rrd_thread: skipping stat recording, as instance is not running"
			time.sleep(self.moninterval)
			

	def get_stat_list(self):
		return self.rrdmonitor.names


	def get_graph(self, idx1, idx2):
		try:
			return self.rrdmonitor.get_graph(idx1, idx2)
		except:
			traceback.print_exc()
		return ""

	def is_instance_running(self):
		f = os.popen('ps ax', 'r')
		running = False
		for l in f:
			if re.search('/vermont', l):
				running = True
				break
		return running


	def start(self):
		if not self.is_instance_running():
			os.system("bash -c 'cd %s; ./vermont -f %s > %s 2>&1 &'" % (self.dir, self.cfgfile, self.logfile))
		return ""
	

	def stop(self):
		if not self.is_instance_running(): return True
		#t = os.popen('ps ax', 'r').read()
		#pid = re.search("\n (\d+).*bash -c ./vermont -f", t).groups()[0]
		os.system("killall vermont")
		for i in range(1,15):
			time.sleep(1)
			if not self.is_instance_running(): return True
		os.system("killall -9 vermont")
		for i in range(1,10):
			time.sleep(1)
			if not self.is_instance_running(): return True
		return False
	

	def reload(self):
		if not self.is_instance_running(): return True
		os.system("killall -USR1 vermont")
		return True


	def get_stats(self):
		try:
			f = open("%s/sensor_output.xml" % self.dir)
			t = f.read()
			f.close()
			return t
		except:
			traceback.print_exc()
		return ""
	

	def get_logfile(self):
		try:
			f = open("%s/%s" % (self.dir, self.logfile))
			t = f.read()
			f.close()
			return t
		except:
			traceback.print_exc()
		return ""
	

	def get_config(self):
		try:
			print "get_config: from %s" % ("%s/%s" % (self.dir, self.cfgfile))
			f = open("%s/%s" % (self.dir, self.cfgfile))
			t = f.read()
			f.close()
			return t
		except:
			traceback.print_exc()
		return ""
			

	def save_config(self, config):
		try:
			f = open("%s/%s" % (self.dir, self.cfgfile), "w")
			f.write(config)
			f.close()
		except:
			traceback.print_exc()
		return ""


class VMRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):

	allowedIp = None

	def verify_request(self, request, client_address):
		return client_address[0]==self.allowedIp


server = VMRPCServer(("", 8000))
server.allow_reuse_address = True
vm = VermontManager()
server.allowedIp = vm.allowedIp
server.register_instance(vm)
thread.start_new_thread(VermontManager.rrd_thread, (vm, ))
server.serve_forever()
