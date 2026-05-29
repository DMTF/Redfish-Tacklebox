#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2026 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Component Integrity

File : rf_component_integrity.py

Brief : This script uses the redfish_utilities module to manage component integrity
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
argget = argparse.ArgumentParser(description="A tool to manage component integrity on a Redfish service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
subparsers = argget.add_subparsers(dest="command")
subparsers.add_parser("list", help="Displays a list of component integrity instances")
getsignedmeasurements_argget = subparsers.add_parser(
    "getsignedmeasurements", help="Gets signed measurements for a component integrity instance"
)
getsignedmeasurements_argget.add_argument(
    "--componentintegrity",
    "-ci",
    type=str,
    required=True,
    help="The identifier of the component integrity instance to collect",
)
getsignedmeasurements_argget.add_argument(
    "--verify",
    "-v",
    action="store_true",
    help="Indicates if the signed measurements should be verified",
)
args = argget.parse_args()

if args.debug:
    log_file = "rf_component_integrity-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_component_integrity Trace")

# Set up the Redfish object
redfish_obj = None
try:
    redfish_obj = redfish.redfish_client(
        base_url=args.rhost, username=args.user, password=args.password, timeout=15, max_retry=3
    )
    redfish_obj.login(auth="session")
except RedfishPasswordChangeRequiredError:
    redfish_utilities.print_password_change_required_and_logout(redfish_obj, args)
    sys.exit(1)
except Exception:
    raise

exit_code = 0
try:
    if args.command == "getsignedmeasurements":
        response, action_context = redfish_utilities.get_signed_measurements(redfish_obj, args.componentintegrity)
        response = redfish_utilities.poll_task_monitor(redfish_obj, response)
        parsed_measurements = redfish_utilities.parse_signed_measurements(response, action_context)
        if args.verify:
            redfish_utilities.verify_signed_measurements(redfish_obj, parsed_measurements)
        redfish_utilities.print_signed_measurements(parsed_measurements)
    else:
        component_integrity_summary = redfish_utilities.get_component_integrity_summary(redfish_obj)
        redfish_utilities.print_component_integrity_summary(component_integrity_summary)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
