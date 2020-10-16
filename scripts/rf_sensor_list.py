#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Sensor List

File : rf_sensor_list.py

Brief : This script uses the redfish_utilities module to dump sensor info
"""

import argparse
import redfish
import redfish_utilities

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to walk a Redfish service and list sensor info" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
args = argget.parse_args()

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

try:
    # Get and print the sensor info
    sensors = redfish_utilities.get_sensors( redfish_obj )
    redfish_utilities.print_sensors( sensors )
finally:
    # Log out
    redfish_obj.logout()
