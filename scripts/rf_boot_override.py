#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Boot Override

File : rf_boot_override.py

Brief : This script uses the redfish_utilities module to manage a one time boot
        override of a system
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to perform a one time boot override of a system" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--system", "-s", type = str, help = "The ID of the system to set" )
argget.add_argument( "--info", "-info", action = "store_true", help = "Indicates if boot information should be reported" )
argget.add_argument( "--target", "-t", type = str, help = "The target boot device; if this argument is omitted the tool will display the current boot settings" )
argget.add_argument( "--uefi", "-uefi", type = str, help = "If target is 'UefiTarget', the UEFI Device Path of the device to boot.  If target is 'UefiBootNext', the UEFI Boot Option string of the device to boot." )
argget.add_argument( "--mode", "-m", type = str, help = "The requested boot mode ('UEFI' or 'Legacy')" )
argget.add_argument( "--reset", "-reset", action = "store_true", help = "Signifies that the system is reset after the boot override is set" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

# Verify the combination of arguments is correct
if args.target is None:
    args.info = True
    if args.uefi or args.mode or args.reset:
        argget.error( "Cannot use '--uefi', '--mode', or '--reset' without '--target'" )

if args.debug:
    log_file = "rf_boot_override-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_boot_override Trace" )

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

exit_code = 0
try:
    if args.info:
        boot = redfish_utilities.get_system_boot( redfish_obj, args.system )
        redfish_utilities.print_system_boot( boot )
    else:
        # Build and send the boot request based on the arguments given
        uefi_target = None
        boot_next = None
        boot_enable = "Once"
        if args.target == "UefiTarget":
            uefi_target = args.uefi
        if args.target == "UefiBootNext":
            boot_next = args.uefi
        if args.target == "None":
            print( "Disabling one time boot..." )
            boot_enable = "Disabled"
        else:
            print( "Setting a one time boot for {}...".format( args.target ) )
        redfish_utilities.set_system_boot( redfish_obj, args.system, args.target, boot_enable, args.mode, uefi_target, boot_next )

        # Reset the system if requested
        if args.reset:
            print( "Resetting the system..." )
            response = redfish_utilities.system_reset( redfish_obj, args.system )
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