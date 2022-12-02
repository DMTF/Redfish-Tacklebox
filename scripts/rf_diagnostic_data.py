#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Diagnostic Data

File : rf_diagnostic_data.py

Brief : This script uses the redfish_utilities module to collect diagnostic data from a log service
"""

import argparse
import datetime
import logging
import os
import redfish
import redfish_utilities
import traceback

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to collect diagnostic data from a log service on a Redfish service" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--manager", "-m", type = str, nargs = "?", default = False, help = "The ID of the manager containing the log service" )
argget.add_argument( "--system", "-s", type = str, nargs = "?", default = False, help = "The ID of the system containing the log service" )
argget.add_argument( "--chassis", "-c", type = str, nargs = "?", default = False, help = "The ID of the chassis containing the log service" )
argget.add_argument( "--log", "-l", type = str, help = "The ID of the log service" )
argget.add_argument( "--type", "-type", type = redfish_utilities.diagnostic_data_types, help = "The type of diagnostic data to collect; defaults to 'Manager' if not specified", choices = redfish_utilities.diagnostic_data_types, default = redfish_utilities.diagnostic_data_types.MANAGER )
argget.add_argument( "--oemtype", "-oemtype", type = str, help = "The OEM-specific type of diagnostic data to collect; this option should only be used if the requested type is 'OEM'" )
argget.add_argument( "--directory", "-d", type = str, help = "The directory to save the diagnostic data; defaults to the current directory if not specified", default = "." )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

# Determine the target log service based on the inputs
# Effectively if the user gives multiple targets, some will be ignored
container_type = redfish_utilities.log_container.MANAGER
container_id = None
if args.manager != False:
    container_type = redfish_utilities.log_container.MANAGER
    container_id = args.manager
elif args.system != False:
    container_type = redfish_utilities.log_container.SYSTEM
    container_id = args.system
elif args.chassis != False:
    container_type = redfish_utilities.log_container.CHASSIS
    container_id = args.chassis

if args.debug:
    log_file = "rf_diagnostic_data-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_diagnostic_data Trace" )

# Set up the Redfish object
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

exit_code = 0
try:
    print( "Collecting diagnostic data..." )
    response = redfish_utilities.collect_diagnostic_data( redfish_obj, container_type, container_id, args.log, args.type, args.oemtype )
    response = redfish_utilities.poll_task_monitor( redfish_obj, response )
    filename, data = redfish_utilities.download_diagnostic_data( redfish_obj, response )

    # Save the file
    if not os.path.isdir( args.directory ):
        os.makedirs( args.directory )
    path = os.path.join( args.directory, filename )
    name_parts = filename.split( ".", 1 )
    file_check = 0
    if len( name_parts ) == 1:
        name_parts.append( "" )
    while os.path.isfile( path ):
        # If the file already exists, build a new file name with a counter
        file_check = file_check + 1
        filename = "{}({}).{}".format( name_parts[0], file_check, name_parts[1] )
        path = os.path.join( args.directory, filename )
    with open( path, "wb" ) as file:
        file.write( data )
    print( "Saved diagnostic data to '{}'".format( path ) )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    redfish_obj.logout()
exit( exit_code )
