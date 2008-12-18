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
import time
import traceback
import sys

from VermontInstance import VermontInstance
from VermontLogger import logger



class LocalVermontInstance(VermontInstance):
    """
    represents a local instance of vermont
    all temporary files are stored at vermonts local directory 
    """

    dir = None
    cfgfile = None
    dyncfgfile = None
    logfile = None
    pid = None


    def __init__(self, directory, cfgfile, logfile, parsexml):
        VermontInstance.__init__(self, parsexml)
        self.dir = directory
        self.cfgfile = cfgfile
        
        self.dyncfgfile = "%s.dynconf" % (cfgfile)
        self.logfile = logfile
        self.pid = 0

        self.retrieveConfig()
        self.syncConfig()

        
    def __str__(self):
        return "<local at dir '%s'>" % self.dir


    def _retrieveConfig(self):
        f = open("%s/%s" % (self.dir, self.cfgfile))
        t = f.read()
        f.close()
        return t
    
    
    def _retrieveDynConfig(self):
        f = open("%s/%s" % (self.dir, self.dyncfgfile))
        t = f.read()
        f.close()
        return t


    def _retrieveSensorData(self):
        f = open("%s/sensor_output.xml" % (self.dir))
        t = f.read()
        f.close()
        return t
            
            
    def _transmitConfig(self):
        f = open("%s/%s" % (self.dir, self.cfgfile), "w")
        f.write(self.cfgText)
        f.close()
        self.cfgModified = False            
            
            
    def _transmitDynConfig(self):
        f = open("%s/%s" % (self.dir, self.dyncfgfile), "w")
        f.write(self.dynCfgText)
        f.write("\n")
        f.close()
        self.cfgModified = False
        
        
    def retrieveLog(self):
        f = open("%s/%s" % (self.dir, self.logfile))
        self.logText = f.read()
        f.close()
        
        
    def retrieveStatus(self):        
        if self.pid != 0:
            # cleanup zombie process, if found ...
            try:
                (pid, ) = os.waitpid(self.pid, os.WNOHANG)
                if self.pid==pid:
                    self.pid = 0
            except: #IGNORE:W0704
                pass
            if os.access("/proc/%d" % self.pid, os.F_OK):
                self.running = True
            else:
                self.running = False
                self.pid = 0
        else:
            self.running = False
        logger().debug("LocalVermontInstance.retrieveStatus: instance running: %s, pid: %d" % (self.running, self.pid))
        
        
    def reload(self):
        logger().debug("LocalVermontInstance.reload()")
        self.retrieveStatus()
        if not self.running:
            return
        
        os.kill(self.pid, 10) # send SIGUSR1 to vermont
    
    
    def start(self):
        logger().debug("LocalVermontInstance.start()")
        self.retrieveStatus()
        if self.running:
            return
        
        cmdline = [ "vermont", "-f", self.dyncfgfile, "-d" ] 
        logger().info("Vermont args: %s" % cmdline)
        logger().info("Truncating log file %s" % self.logfile)
        f = os.open(self.logfile, os.O_CREAT|os.O_TRUNC)
        os.close(f)
        
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
            try:
                os.execv("./vermont", cmdline)
            except:
                logger().error(traceback.format_exc())
            sys.stderr.write("Problem starting Vermont, exiting forked process ...\n")
            os._exit(1)
        else:
            logger().debug("PID of started vermont: %d" % pid)
            self.pid = pid

        
    def stop(self):
        logger().debug("LocalVermontInstance.stop()")
        self.retrieveStatus()
        if not self.running:
            return True

        try:
            os.kill(self.pid, 2)
            for _ in range(1,15):
                time.sleep(1)
                pid, _ = os.waitpid(self.pid, os.WNOHANG)
                if self.pid==pid:
                    self.pid = 0
                    return True
            os.kill(self.pid, 9)            
            for _ in range(1,10):
                time.sleep(1)
                pid, _ = os.waitpid(self.pid, os.WNOHANG)
                if self.pid==pid:
                    self.pid = 0
                    return True
            
        except:
            logger().error(traceback.format_exc())
        return False
