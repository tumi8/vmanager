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
import os
from Ft.Xml.Domlette import NonvalidatingReader

from VermontInstance import VermontInstance



class LocalVermontInstance(VermontInstance):
    "represents a local instance of vermont"

    dir = None
    cfgfile = None
    dyncfgfile = None
    logfile = None
    pid = None


    def __init__(self, dir, cfgfile):
        VermontInstance.__init__(self)
        self.dir = dir
        self.cfgfile = "%s/%s" % (dir, cfgfile)
        self.dyncfgfile = "%s/vmanager.dyn.conf" % dir
        self.logfile = "%s/vmanager.log" % dir
        self.pid = 0

        self.retrieveConfig()
        
        
    def __str__(self):
        return "<local at dir '%s'>" % self.dir


    def _retrieveConfig(self):
        f = open(self.cfgfile)
        t = f.read()
        f.close()
        return t
    
    
    def _retrieveDynConfig(self):
        f = open(self.dyncfgfile)
        t = f.read()
        f.close()
        return t


    def _retrieveSensorData(self):
        f = open("%s/sensor_output.xml" % (self.dir))
        t = f.read()
        f.close()
        return t
            
            
    def _transmitConfig(self):
        f = open(self.cfgfile, "w")
        f.write(self._cfgText)
        f.close()
        self._cfgModified = False            
            
            
    def _transmitDynConfig(self):
        f = open(self.dyncfgfile, "w")
        f.write(self._dynCfgText)
        f.write("\n")
        f.close()
        self._cfgModified = False
        
        
    def retrieveLog(self):
        f = open(self.logfile)
        t = f.read()
        f.close()
        return t
        
        
    def running(self):
       return pid != 0
        
        
    def reload(self):
        if not self.running():
            return
        
        os.kill(pid, 1) # send SIGHUP to vermont
    
    
    def start(self):
        if self.running():
            return
        
        pid = os.fork()
        if pid == 0: 
            maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
            if (maxfd == resource.RLIM_INFINITY):
                maxfd = MAXFD

            REDIRECT_TO = self.logfile
            # Iterate through and close all file descriptors.
            for fd in range(0, maxfd):
                try:
                    os.close(fd)
                except:
                    pass
            os.open(REDIRECT_TO, os.O_RDWR)
            os.dup2(0, 1)
            os.dup2(0, 2)
            os.chdir(self.dir)
            os.execl("./vermont", "-f", self.dyncfgfile)
        else:
            sys.stderr.write("PID=%d\n" % pid)
            self.pid = pid

        
    def stop(self):
        if not self.running():
            return True

        kill(2, self.pid)
        for i in range(1,15):
            time.sleep(1)
            (pid, status) = os.waitpid(self.pid, WNOHANG)
            if self.pid==pid:
                self.pid = 0
                return True
        kill(9, self.pid)
        for i in range(1,10):
            time.sleep(1)
            (pid, status) = os.waitpid(self.pid, WNOHANG)
            if self.pid==pid:
                self.pid = 0
                return True
        return False
