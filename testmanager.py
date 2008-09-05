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

import os
import sys
import time
import logging

d = os.path.dirname(sys.argv[0])
sys.path.insert(0, d + 'common')
sys.path.insert(0, d + 'controller')
sys.path.insert(0, d + 'webinterface')

import LocalVermontInstance
import VermontConfigurator
import VermontInstanceManager
import VermontLogger


VermontLogger.init("testapp", "tmp/test.log", True)
VermontLogger.logger().info("starting test")
lvi = LocalVermontInstance.LocalVermontInstance("tmp", "tmp.conf", "tmp.log", True)
vim = VermontInstanceManager.VermontInstanceManager("tmp", False)
vim.vermontInstances = (lvi)
vim._checkInterval = 5

vc = VermontConfigurator.VermontConfigurator()
vc.parseConfigs([lvi])
vim.vermontInstances = [lvi]
vim._configurator = vc

vim.startConfigThread()
time.sleep(10)
