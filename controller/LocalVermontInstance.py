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


import os
import resource
import sys
import time

from VermontInstance import VermontInstance



class LocalVermontInstance(VermontInstance):
    "represents a local instance of vermont"

    dir = None
    cfgfile = None
    dyncfgfile = None
    logfile = None
    pid = None


    def __init__(self, directory, cfgfile, logfile, parsexml):
        VermontInstance.__init__(self, parsexml)
        self.dir = directory
        self.cfgfile = "%s/%s" % (dir, cfgfile)
        self.dyncfgfile = "%s/%s.dynconf" % (dir, cfgfile)
        self.logfile = "%s/%s" % (dir, logfile)
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
        self.cfgModified = False            
            
            
    def _transmitDynConfig(self):
        f = open(self.dyncfgfile, "w")
        f.write(self._dynCfgText)
        f.write("\n")
        f.close()
        self.cfgModified = False
        
        
    def retrieveLog(self):
        f = open(self.logfile)
        self.logText = f.read()
        f.close()
        
        
    def running(self):
        return self.pid != 0
        
        
    def reload(self):
        print "LocalVermontInstance.reload()"
        if not self.running():
            return
        
        os.kill(self.pid, 16) # send SIGUSR1 to vermont
    
    
    def start(self):
        print "LocalVermontInstance.start()"
        if self.running():
            return
        
        pid = os.fork()
        if pid == 0: 
            maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
            if (maxfd == resource.RLIM_INFINITY):
                maxfd = os.sysconf('SC_OPEN_MAX')

            REDIRECT_TO = self.logfile
            # Iterate through and close all file descriptors.
            for fd in range(0, maxfd):
                try:
                    os.close(fd)
                except: #IGNORE:W0704
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
        print "LocalVermontInstance.stop()"
        if not self.running():
            return True

        os.kill(2, self.pid)
        for _ in range(1,15):
            time.sleep(1)
            (pid, ) = os.waitpid(self.pid, os.WNOHANG)
            if self.pid==pid:
                self.pid = 0
                return True
        os.kill(9, self.pid)
        for _ in range(1,10):
            time.sleep(1)
            (pid, ) = os.waitpid(self.pid, os.WNOHANG)
            if self.pid==pid:
                self.pid = 0
                return True
        return False
