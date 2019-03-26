#!/usr/bin/env python3
"""env.py - sets environment for boinc-utils and establishes global variables


    Copyright (C) 2019  RueiKe

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
__author__ = "RueiKe"
__copyright__ = "Copyright (C) 2019 RueiKe"
__credits__ = []
__license__ = "GNU General Public License"
__program_name__ = "amdgpu-utils"
__version__ = "v0.0.1"
__maintainer__ = "RueiKe"
__status__ = "Development"

import re
import subprocess
import os
import platform
import sys
import time
import shlex
import shutil
from datetime import datetime


class GUT_CONST:
    def __init__(self):
        self.featuremask = "/sys/module/amdgpu/parameters/ppfeaturemask"
        self.card_root = "/sys/class/drm/"
        self.hwmon_sub = "hwmon/hwmon"
        self.execute_pac = False
        self.DEBUG = False
        self.BOINC_HOME = "/home/boinc/BOINC/"
        self.LOG = False
        self.log_file_ptr = ""
        self.show_fans = True
        self.write_delta_only = False
        self.SLEEP = 2
        self.PATH = "."
        self.amdfeaturemask = ""

    def read_amdfeaturemask(self):
        with open(gut_const.featuremask) as fm_file:
            self.amdfeaturemask = int(fm_file.readline())
            return (self.amdfeaturemask)

    def check_env(self):
        # Check python version
        required_pversion = [3,6]
        (python_major, python_minor, python_patch) = platform.python_version_tuple()
        if self.DEBUG: print("Using python " + python_major +"."+ python_minor +"."+ python_patch)
        if int(python_major) < required_pversion[0]:
            print("Using python" + python_major + ", but " + __program_name__ + 
                    " requires python " + str(required_pversion[0]) +"."+ str(required_pversion[1]) + " or higher.",
                    file=sys.stderr)
            return(-1)
        elif int(python_major) == required_pversion[0] and int(python_minor) < required_pversion[1]:
            print("Using python " + python_major +"."+ python_minor +"."+ python_patch + ", but " + __program_name__ +
                    " requires python " + str(required_pversion[0]) +"."+ str(required_pversion[1]) + " or higher.",
                    file=sys.stderr)
            return(-1)

        # Check Linux Kernel version
        required_kversion = [4,8]
        linux_version = platform.release()
        if int(linux_version.split(".")[0]) < required_kversion[0]:
            print("Using Linux Kernel " +  linux_version + ", but " + __program_name__ + " requires > " +
                    str(required_kversion[0]) +"."+ str(required_kversion[1]), file=sys.stderr)
            return(-2)
        elif int(linux_version.split(".")[0]) == required_kversion[0] and int(linux_version.split(".")[1]) < required_kversion[1]:
            print("Using Linux Kernel " + linux_version + ", but " + __program_name__ + " requires > " + 
                    str(required_kversion[0]) +"."+ str(required_kversion[1]), file=sys.stderr)
            return(-2)

        # Check AMD GPU Driver Version
        lshw_out = subprocess.check_output(shlex.split('lshw -c video'), shell=False,
                stderr=subprocess.DEVNULL).decode().split("\n")
        for lshw_line in lshw_out:
            searchObj = re.search('configuration:', lshw_line)
            if(searchObj != None):
                lineitems = lshw_line.split(sep=':')
                driver_str = lineitems[1].strip()
                searchObj = re.search('driver=amdgpu', driver_str)
                if(searchObj != None):
                    return(0)
                else:
                    print(f"amdgpu-utils non-compatible driver: {driver_str}")
                    return(-3)
        return(0)

    def get_amd_driver_version(self):
        if shutil.which("/usr/bin/dpkg") == None:
            print("can not determine amdgpu version")
            return(-1)
        try:
            dpkg_out = subprocess.check_output(shlex.split('dpkg -l amdgpu'), shell=False,
                    stderr=subprocess.DEVNULL).decode().split("\n")
            for dpkg_line in dpkg_out:
                searchObj = re.search('amdgpu', dpkg_line)
                if(searchObj != None):
                    dpkg_items = dpkg_line.split()
                    print(f"amdgpu version: {dpkg_items[2]}")
        except subprocess.CalledProcessError as e:
            if re.search('exit status 1', str(e)) != None:
                print(str(e))
                print("Warning: amdgpu drivers not may not be installed.")
                return(-1)
                #print("Error: amdgpu drivers not installed, exiting...")
                #sys.exit(-1)
        except:
            print("Warning: Cannot read determine amdgpu version.")
            return(-1)
        return(0)

gut_const = GUT_CONST()
