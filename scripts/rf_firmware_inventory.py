#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Firmware Inventory

File : rf_firmware_inventory.py

Brief : This script uses the redfish_utilities module to manage firmware inventory
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
argget = argparse.ArgumentParser(description="A tool to collect firmware inventory from a Redfish service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument(
    "--details", "-details", action="store_true", help="Indicates details to be shown for each firmware entry"
)
argget.add_argument("--id", "-i", action="store_true", help="Construct inventory names using 'Id' values")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
args = argget.parse_args()

if args.debug:
    log_file = "rf_firmware_inventory-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_firmware_inventory Trace")

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
    firmware_inventory = redfish_utilities.get_firmware_inventory(redfish_obj)
    redfish_utilities.print_software_inventory(firmware_inventory, details=args.details, use_id=args.id)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
