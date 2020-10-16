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
import redfish
import redfish_utilities

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to perform a one time boot override of a system" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--system", "-s", type = str, help = "The ID of the system to set" )
argget.add_argument( "--target", "-t", type = str, help = "The target boot device; if not provided the tool will display the current boot settings" )
argget.add_argument( "--uefi", "-uefi", type = str, help = "If target is 'UefiTarget', the UEFI Device Path of the device to boot.  If target is 'UefiBootNext', the UEFI Boot Option string of the device to boot." )
argget.add_argument( "--reset", "-reset", action = "store_true", help = "Signifies that the system is reset after the boot override is set" )
args = argget.parse_args()

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

try:
    if args.target is None:
        # Target not specified; just get the settings and display them
        boot = redfish_utilities.get_system_boot( redfish_obj, args.system )
        redfish_utilities.print_system_boot( boot )
    else:
        # Build and send the boot request based on the arguments given
        uefi_target = None
        boot_next = None
        boot_mode = "Once"
        if args.target == "UefiTarget":
            uefi_target = args.uefi
        if args.target == "UefiBootNext":
            boot_next = args.uefi
        if args.target == "None":
            print( "Disabling one time boot..." )
            boot_mode = "Disabled"
        else:
            print( "Setting a one time boot for {}...".format( args.target ) )
        redfish_utilities.set_system_boot( redfish_obj, args.system, args.target, boot_mode, None, uefi_target, boot_next )

        # Reset the system if requested
        if args.reset:
            print( "Resetting the system..." )
            response = redfish_utilities.system_reset( redfish_obj, args.system )
            response = redfish_utilities.poll_task_monitor( redfish_obj, response )
            redfish_utilities.verify_response( response )
finally:
    # Log out
    redfish_obj.logout()
