#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Licenses

File : rf_licenses.py

Brief : This script uses the redfish_utilities module to manage licenses
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
argget = argparse.ArgumentParser(description="A tool to manage licenses on a Redfish service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
subparsers = argget.add_subparsers(dest="command")
info_argget = subparsers.add_parser("info", help="Displays information about the licenses installed on the service")
info_argget.add_argument(
    "--details", "-details", action="store_true", help="Indicates if the full details of each license should be shown"
)
install_argget = subparsers.add_parser("install", help="Installs a new license")
install_argget.add_argument(
    "--license", "-l", type=str, required=True, help="The filepath or URI to the license to install"
)
delete_argget = subparsers.add_parser("delete", help="Deletes a license")
delete_argget.add_argument("--license", "-l", type=str, required=True, help="The identifier of the license to delete")
args = argget.parse_args()

if args.debug:
    log_file = "rf_licenses-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_licenses Trace")

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
    if args.command == "install":
        print("Installing license '{}'...".format(args.license))
        response = redfish_utilities.install_license(redfish_obj, args.license)
        response = redfish_utilities.poll_task_monitor(redfish_obj, response)
        redfish_utilities.verify_response(response)
    elif args.command == "delete":
        print("Deleting license '{}'...".format(args.license))
        response = redfish_utilities.delete_license(redfish_obj, args.license)
        response = redfish_utilities.poll_task_monitor(redfish_obj, response)
        redfish_utilities.verify_response(response)
    else:
        licenses = redfish_utilities.get_licenses(redfish_obj)
        if args.command == "info":
            redfish_utilities.print_licenses(licenses, details=args.details)
        else:
            redfish_utilities.print_licenses(licenses)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
