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


import xmlrpclib
import re

class VermontInstance:
	"represents a remote instance of vermont"

	url = None
	online = None
	_conn = None
	host = None
	cfgtext = None
	status = None
	sensorData = None


	def __init__(self, url):
		self.url = url
		self.online = False
		self._conn = xmlrpclib.Server(url, allow_none=True)
		self.host = re.match("http://(.*)[:/$]", url).group(1)
		self.sensorData = ""
		self.checkOnline()
		if online:
			self.get_cfgtext()


	def checkOnline(self):
		try:
			self.online = self._conn.is_instance_running()
		except e:
			self.online = false
			self.status = str(e) 
	

	def get_cfgtext(self):
		self.cfgtext = self._conn.get_config()


	def set_cfgtext(self, text):
		self._conn.save_config(text)
		self.cfgtext = text


	def getSensorData(self):
		if self.online:
			self.sensorData = self._conn.get_stats()
		else:
			self.sensorData = ""