#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Event Service

File : rf_event_service.py

Brief : This script uses the redfish_utilities module to manage the event service and event subscriptions
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback
import sys
from redfish.messages import RedfishPasswordChangeRequiredError

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to manage the event service on a Redfish service" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
subparsers = argget.add_subparsers( dest = "command" )
info_argget = subparsers.add_parser( "info", help = "Displays information about the event service and subscriptions" )
sub_argget = subparsers.add_parser( "subscribe", help = "Creates an event subscription to a specified URL" )
sub_argget.add_argument( "--destination", "-dest", type = str, required = True, help = "The URL where events are sent for the subscription" )
sub_argget.add_argument( "--context", "-c", type = str, help = "The context string for the subscription that is supplied back in the event payload" )
sub_argget.add_argument( "--expand", "-e", action = "store_true", help = "Indicates if the origin of condition in the event is to be expanded", default = None )
sub_argget.add_argument( "--format", "-f", type = str, help = "The format of the event payloads" )
sub_argget.add_argument( "--resourcetypes", "-rt", type = str, nargs = '+', help = "A list of resource types for the subscription" )
sub_argget.add_argument( "--registries", "-reg", type = str, nargs = '+', help = "A list of registries for the subscription" )
sub_argget.add_argument( "--eventtypes", "-et", type = str, nargs = '+', help = "A list of event types for the subscription; this option has been deprecated in favor of other methods such as 'resource types' and 'registries'" )
unsub_argget = subparsers.add_parser( "unsubscribe", help = "Deletes an event subscription" )
unsub_argget.add_argument( "--id", "-i", type = str, required = True, help = "The identifier of the event subscription to be deleted" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_event_service-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_event_service Trace" )

# Set up the Redfish object
try:
    redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password , timeout=5, max_retry=3)
    redfish_obj.login( auth = "session" )
except RedfishPasswordChangeRequiredError as e:
    print("Password change required\n run rf_accounts.py -r {} -u {} -p <old password> --setpassword {} <new password> \nto set your password\n".format(args.rhost ,args.user, args.user))
    try:
        redfish_obj.logout()
    except Exception as e:
        pass
    sys.exit(1)
except Exception as e:
    # other error
    error_string = str(e)
    if len(error_string) > 0:
        print("{}\nLogin Failed\n".format(error_string))
    else:
        print("Login Failed\n")
    try:
        redfish_obj.logout()
    except Exception as e:
        pass
    sys.exit(1)

exit_code = 0
try:
    if args.command == "subscribe":
        response = redfish_utilities.create_event_subscription( redfish_obj, args.destination, format = args.format, client_context = args.context,
            expand = args.expand, resource_types = args.resourcetypes, registries = args.registries, event_types = args.eventtypes )
        print( "Created subscription '{}'".format( response.getheader( "Location" ) ) )
    elif args.command == "unsubscribe":
        print( "Deleting subscription '{}'".format( args.id ) )
        redfish_utilities.delete_event_subscription( redfish_obj, args.id )
    else:
        event_service = redfish_utilities.get_event_service( redfish_obj )
        redfish_utilities.print_event_service( event_service )
        print( "" )
        event_subscriptions = redfish_utilities.get_event_subscriptions( redfish_obj )
        redfish_utilities.print_event_subscriptions( event_subscriptions )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    try:
        redfish_obj.logout()
    except Exception as e:
        pass
sys.exit( exit_code )
