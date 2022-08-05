#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Resets Module

File : resets.py

Brief : This file contains the common definitions and functionalities for
        reset operations
"""

reset_types = [ "On", "ForceOff", "GracefulShutdown", "GracefulRestart", "ForceRestart", "Nmi", "ForceOn",
                "PushPowerButton", "PowerCycle", "Suspend", "Pause", "Resume" ]
