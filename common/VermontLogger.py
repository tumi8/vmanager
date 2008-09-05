# Vermont Management
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


import logging
import sys

__logger = None



def logger():
    return  __logger


def init(appname, logfile, tostderr):
    global __logger  #IGNORE:W0603
    __logger = logging.getLogger(appname)
    __logger.handlers = []
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    if logfile is not None and logfile != "":
        hdlr = logging.FileHandler(logfile)    
        hdlr.setFormatter(formatter)
        __logger.addHandler(hdlr)
    if tostderr:
        hdstd = logging.StreamHandler(sys.stderr)
        hdstd.setFormatter(formatter)
        __logger.addHandler(hdstd)
    
    __logger.setLevel(logging.DEBUG)
