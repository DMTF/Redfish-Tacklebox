#! /usr/bin/python
# Copyright Notice:
# Copyright 2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Power Reset

File : rf_power_reset

Brief : This script uses the redfish_utilities module to perform a reset of the system
"""

import argparse
import redfish
import redfish_utilities

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to perform a power/reset operation of a system" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--system", "-s", type = str, help = "The ID of the system perform the operation" )
argget.add_argument( "--type", "-t", type = str, help = "The type of power/reset operation to perform" )
args = argget.parse_args()

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

try:
    print( "Resetting the system..." )
    response = redfish_utilities.system_reset( redfish_obj, args.system, args.type )
    response = redfish_utilities.poll_task_monitor( redfish_obj, response )
    redfish_utilities.verify_response( response )
finally:
    # Log out
    redfish_obj.logout()
