#!/usr/bin/env python3
"""BOINCmodules  -  classes used in boinc-utils


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
__program_name__ = "boinc-utils"
__version__ = "v0.0.1"
__maintainer__ = "RueiKe"
__status__ = "Development"

import re
import subprocess
import shlex
import socket
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import glob 
import shutil 
try:
    from BOINCmodules import env 
except:
    import env 


class TASK_ITEM:
    """An object to store Task details."""
    def __init__(self, item_id):
        self.uuid = item_id
        self.params = {
        "name" : "",
        "WU name" : "",
        "project URL" : "",
        "received" : "",
        "report deadline" : "",
        "ready to report" : "",
        "got server ack" : "",
        "final CPU time" : -1,
        "state" : "",
        "scheduler state" : "",
        "exit_status" : -1,
        "signal" : -1,
        "suspended via GUI" : "",
        "active_task_state" : "",
        "app version num" : "",
        "checkpoint CPU time" : -1,
        "current CPU time" : -1,
        "fraction done" : -1,
        "swap size" : "",
        "working set size" : "",
        "estimated CPU time remaining" : -1
        }

    def set_params_value(self, name, value):
        # update params dictionary
        self.params[name] = value

    def get_params_value(self, name):
        # reads params dictionary
        return(self.params[name])

    def get_all_params_labels(self):
        Task_Param_Labels = [ "name", "WU name", "project URL", "received", "report deadline", "ready to report",
                "got server ack", "final CPU time", "state", "scheduler state", "exit_status", "signal", "suspended via GUI",
                "active_task_state", "app version num", "checkpoint CPU time", "current CPU time", "fraction done",
                "swap size", "working set size", "estimated CPU time remaining" ]
        return(Task_Param_Labels)

    def print(self):
        for k in self.get_all_params_labels():
            print(k +": "+ str(self.get_params_value(k)))
        print("")


    def uhang_task(self):
        # Pause then resume the task
        #./boinccmd --task http://setiathome.berkeley.edu/ blc23_2bit_guppi_58405_84300_HIP86137_0023.6158.0.22.45.76.vlar_0 suspend
        #./boinccmd --task http://setiathome.berkeley.edu/ blc23_2bit_guppi_58405_84300_HIP86137_0023.6158.0.22.45.76.vlar_0 resume
        boinccmd  = os.path.join(env.gut_const.BOINC_HOME, "boinccmd") + " --task " + self.get_params_value("project URL") + " " + self.get_params_value("name") 
        try:
            cmd = subprocess.Popen(shlex.split(boinccmd + " suspend"), shell=False, stderr=subprocess.DEVNULL)
            output = cmd.stdout.read()
            cmd.stdout.close()
            cmd.wait()
            cmd = subprocess.Popen(shlex.split(boinccmd + " resume"), shell=False, stderr=subprocess.DEVNULL)
            output = cmd.stdout.read()
            cmd.stdout.close()
            cmd.wait()
        except:
            print("Error: could not execute boinccmd: %s", boinccmd)
        return


class TASK_LIST:
    """A list of TASK_ITEMS indexed with uuid."""
    def __init__(self):
        self.list = {}

    def read_task_list(self):
        """ This method should be the first called to popultate the list of tasks.
        """
        task_flag = False
        new_task = False
        boinccmd  = os.path.join(env.gut_const.BOINC_HOME, "boinccmd")
        task_list = subprocess.check_output(shlex.split(boinccmd + ' --get_simple_gui_info'), shell=False,
                stderr=subprocess.DEVNULL).decode().split("\n")
        for task_line in task_list:
            if task_flag == False:
                if task_line[:14] == "======== Tasks":
                    task_flag = True
                continue

            stask_line = task_line.strip()
            if re.fullmatch(r'[0-9]+\).*', task_line):
                new_task = True
                task_item = TASK_ITEM(uuid4().hex)
                self.list[task_item.uuid] = task_item
                continue
            task_items = stask_line.split(': ')
            if len(task_items) == 2:
                task_item.set_params_value(task_items[0],  task_items[1])

    def get_fd_for_wu(self, wu):
        for k, v in self.list.items():
            if v.get_params_value("WU name") == wu:
                return(v.get_params_value("fraction done"))

    def find_hung_task(self, t_minus1):
        for k, v in self.list.items():
            if v.get_params_value("active_task_state") != "EXECUTING":
                continue
            if float(v.get_params_value("fraction done")) < 0.0002:
                continue
            wu = v.get_params_value("WU name")
            tm1 = t_minus1.get_fd_for_wu(wu)
            fd = v.get_params_value("fraction done")
            if tm1 == fd:
                print("%s: Hung Task: %s, fraction done: %s, app: %s" %
                        t.strftime('%m%d_%H%M%S'), wu, fd, v.get_params_value("app version num"))
                v.uhang_task()

    def print(self):
        for k, v in self.list.items():
            v.print()


def test():
    #env.gut_const.DEBUG = True


    task_list = TASK_LIST()
    task_list.read_task_list()
    task_list.print()
    exit()


if __name__ == "__main__":
    test()

