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
import datetime
import logging
import redfish
import redfish_utilities
import traceback

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to walk a Redfish service and list component information" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--details", "-details", action = "store_true", help = "Indicates if the full details of each component should be shown" )
argget.add_argument( "--noabsent", "-noabsent", action = "store_true", help = "Indicates if absent devices should be skipped" )
argget.add_argument( "--write", "-w", nargs = "?", const = "Device_Inventory", type = str, help = "Indicates if the inventory should be written to a spreadsheet and what the file name should be if given" )
argget.add_argument( "--workaround", "-workaround", action = "store_true", help = "Indicates if workarounds should be attempted for non-conformant services", default = False )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

if args.workaround:
    redfish_utilities.config.__workarounds__ = True

if args.debug:
    log_file = "rf_sys_inventory-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_sys_inventory Trace" )

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

exit_code = 0
try:
    # Get and print the system inventory
    inventory = redfish_utilities.get_system_inventory( redfish_obj )
    redfish_utilities.print_system_inventory( inventory, args.details, args.noabsent )

    if args.write:
        redfish_utilities.write_system_inventory( inventory, args.write )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    redfish_obj.logout()
exit( exit_code )
