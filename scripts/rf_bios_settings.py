#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish BIOS Settings

File : rf_bios_settings.py

Brief : This script uses the redfish_utilities module to manager BIOS settings of a system
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to manager BIOS settings for a system" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--system", "-s", type = str, help = "The ID of the system to manage" )
argget.add_argument( "--attribute", "-a", type = str, nargs = 2, metavar = ( "name", "value" ), action = "append", help = "Sets a BIOS attribute to a new value; can be supplied multiple times to set multiple attributes" )
argget.add_argument( "--workaround", "-workaround", action = "store_true", help = "Indicates if workarounds should be attempted for non-conformant services", default = False )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

if args.workaround:
    redfish_utilities.config.__workarounds__ = True

if args.debug:
    log_file = "rf_bios_settings-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_bios_settings Trace" )

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

exit_code = 0
try:
    # Get the BIOS settings
    current_settings, future_settings = redfish_utilities.get_system_bios( redfish_obj, args.system )

    if args.attribute is not None:
        new_settings = {}
        for attribute in args.attribute:
            # Based on the current settings, determine the appropriate data type for the new setting
            new_value = attribute[1]
            if attribute[0] in current_settings:
                if isinstance( current_settings[attribute[0]], bool ):
                    # Boolean; convert from a string
                    if new_value.lower() == "true":
                        new_value = True
                    else:
                        new_value = False
                elif isinstance( current_settings[attribute[0]], ( int, float ) ):
                    # Integer or float; go by the user input to determine how to convert since the current value may be truncated
                    try:
                        new_value = int( new_value )
                    except:
                        new_value = float( new_value )

            # Set the specified attribute to the new value
            new_settings[attribute[0]] = new_value
            print( "Setting {} to {}...".format( attribute[0], attribute[1] ) )
        redfish_utilities.set_system_bios( redfish_obj, new_settings, args.system )
    else:
        # Print the BIOS settings
        redfish_utilities.print_system_bios( current_settings, future_settings )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    redfish_obj.logout()
exit( exit_code )
