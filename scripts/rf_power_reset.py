#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Power Reset

File : rf_power_reset.py

Brief : This script uses the redfish_utilities module to perform a reset of the system
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to perform a power/reset operation of a system" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--system", "-s", type = str, help = "The ID of the system to reset" )
argget.add_argument( "--type", "-t", type = str, help = "The type of power/reset operation to perform", choices = redfish_utilities.reset_types )
argget.add_argument( "--info", "-info", action = "store_true", help = "Indicates if reset and power information should be reported" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_power_reset-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_power_reset Trace" )

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

exit_code = 0
try:
    if args.info:
        system_info = redfish_utilities.get_system( redfish_obj, args.system )
        reset_uri, reset_parameters = redfish_utilities.get_system_reset_info( redfish_obj, args.system, system_info )
        printed_reset_types = False
        for param in reset_parameters:
            if param["Name"] == "ResetType" and "AllowableValues" in param:
                print( "Supported reset types: {}".format( ", ".join( param["AllowableValues"] ) ) )
                printed_reset_types = True
        if not printed_reset_types:
            print( "No reset information found" )
        if "PowerState" in system_info.dict:
            print( "Current power state: {}".format( system_info.dict["PowerState"] ) )
        else:
            print( "No power state information found" )
    else:
        print( "Resetting the system..." )
        response = redfish_utilities.system_reset( redfish_obj, args.system, args.type )
        response = redfish_utilities.poll_task_monitor( redfish_obj, response )
        redfish_utilities.verify_response( response )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    redfish_obj.logout()
exit( exit_code )
