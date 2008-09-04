#!/usr/bin/python


import os
import re
import sys
import ConfigParser
import traceback
import time
import thread
from Ft.Xml.Domlette import NonvalidatingReader
import base64



class VermontManager:

	dir = None
	cfgfile = None
	logfile = None
	rrdmonitor = None
	moninterval = None
	allowedIp = None

	def __init__(self):
	
		
		self.rrdmonitor = RRDVermontMonitor(xpaths, names, self.moninterval)

			

	def get_stat_list(self):
		return self.rrdmonitor.names


	def get_graph(self, idx1, idx2):
		try:
			return self.rrdmonitor.get_graph(idx1, idx2)
		except:
			traceback.print_exc()
		return ""


	

