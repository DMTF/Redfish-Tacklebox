#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish System Inventory

File : rf_sys_inventory.py

Brief : This script uses the redfish_utilities module to dump system inventory
        information
"""

import argparse
import redfish
import redfish_utilities

import json

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to walk a Redfish service and list component information" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--details", "-details", action = "store_true", help = "Indicates if the full details of each component should be shown" )
argget.add_argument( "--noabsent", "-noabsent", action = "store_true", help = "Indicates if absent devices should be skipped" )
argget.add_argument( "--write", "-w", nargs = "?", const = "Device_Inventory", type = str, help = "Indicates if the inventory should be written to a spreadsheet and what the file name should be if given" )
args = argget.parse_args()

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

try:
    # Get and print the system inventory
    inventory = redfish_utilities.get_system_inventory( redfish_obj )
    redfish_utilities.print_system_inventory( inventory, details = args.details, skip_absent = args.noabsent )

    if( args.write ):
        redfish_utilities.write_system_inventory( inventory, args.write )

finally:
    # Log out
    redfish_obj.logout()
