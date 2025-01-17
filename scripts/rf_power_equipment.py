#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Power Equipment

File : rf_power_equipment.py

Brief : This script uses the redfish_utilities module to manage power equipment
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
argget = argparse.ArgumentParser(description="A tool to manage power equipment")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
subparsers = argget.add_subparsers(dest="command")
list_argget = subparsers.add_parser("list", help="Displays a list of the available power equipment")
status_argget = subparsers.add_parser("status", help="Displays the status of an instance of power equipment")
status_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.power_equipment_types,
    required=True,
    help="The type of power equipment to get",
    choices=redfish_utilities.power_equipment_types,
)
status_argget.add_argument("--equipment", "-pe", type=str, help="The identifier of the power equipment to get")
outletsummary_argget = subparsers.add_parser(
    "outlets", help="Displays the outlet summary of an instance of power equipment"
)
outletsummary_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.power_equipment_types,
    required=True,
    help="The type of power equipment to get",
    choices=redfish_utilities.power_equipment_types,
)
outletsummary_argget.add_argument("--equipment", "-pe", type=str, help="The identifier of the power equipment to get")
outlet_info_argget = subparsers.add_parser(
    "outletinfo", help="Displays the status of an outlet for an instance of power equipment"
)
outlet_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.power_equipment_types,
    required=True,
    help="The type of power equipment to get",
    choices=redfish_utilities.power_equipment_types,
)
outlet_info_argget.add_argument("--equipment", "-pe", type=str, help="The identifier of the power equipment to get")
outlet_info_argget.add_argument("--outlet", "-o", type=str, help="The identifier of the outlet to get")
mains_info_argget = subparsers.add_parser(
    "mainsinfo", help="Displays the status of a mains circuit for an instance of power equipment"
)
mains_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.power_equipment_types,
    required=True,
    help="The type of power equipment to get",
    choices=redfish_utilities.power_equipment_types,
)
mains_info_argget.add_argument("--equipment", "-pe", type=str, help="The identifier of the power equipment to get")
mains_info_argget.add_argument("--mains", "-m", type=str, help="The identifier of the mains circuit to get")
branch_info_argget = subparsers.add_parser(
    "branchinfo", help="Displays the status of a branch circuit for an instance of power equipment"
)
branch_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.power_equipment_types,
    required=True,
    help="The type of power equipment to get",
    choices=redfish_utilities.power_equipment_types,
)
branch_info_argget.add_argument("--equipment", "-pe", type=str, help="The identifier of the power equipment to get")
branch_info_argget.add_argument("--branch", "-b", type=str, help="The identifier of the branch circuit to get")
args = argget.parse_args()

if args.debug:
    log_file = "rf_power_equipment-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_power_equipment Trace")

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
    if args.command == "status":
        power_equipment = redfish_utilities.get_power_equipment(
            redfish_obj,
            args.type,
            args.equipment,
            get_metrics=True,
            get_mains=True,
            get_branches=True,
            get_feeders=True,
            get_subfeeds=True,
        )
        redfish_utilities.print_power_equipment(power_equipment)
        circuit_types = [
            redfish_utilities.power_equipment_electrical_types.MAINS,
            redfish_utilities.power_equipment_electrical_types.BRANCH,
            redfish_utilities.power_equipment_electrical_types.FEEDER,
            redfish_utilities.power_equipment_electrical_types.SUBFEED,
        ]
        for circuit_type in circuit_types:
            redfish_utilities.print_power_equipment_electrical_summary(power_equipment, circuit_type, False)
    elif args.command == "outlets":
        power_equipment = redfish_utilities.get_power_equipment(
            redfish_obj, args.type, args.equipment, get_outlets=True
        )
        redfish_utilities.print_power_equipment_electrical_summary(
            power_equipment, redfish_utilities.power_equipment_electrical_types.OUTLET, True
        )
    elif args.command == "outletinfo":
        outlet = redfish_utilities.get_power_equipment_electrical(
            redfish_obj,
            args.type,
            redfish_utilities.power_equipment_electrical_types.OUTLET,
            args.equipment,
            args.outlet,
        )
        redfish_utilities.print_power_equipment_electrical(outlet)
    elif args.command == "mainsinfo":
        mains = redfish_utilities.get_power_equipment_electrical(
            redfish_obj, args.type, redfish_utilities.power_equipment_electrical_types.MAINS, args.equipment, args.mains
        )
        redfish_utilities.print_power_equipment_electrical(mains)
    elif args.command == "branchinfo":
        mains = redfish_utilities.get_power_equipment_electrical(
            redfish_obj,
            args.type,
            redfish_utilities.power_equipment_electrical_types.BRANCH,
            args.equipment,
            args.branch,
        )
        redfish_utilities.print_power_equipment_electrical(mains)
    else:
        power_equipment = redfish_utilities.get_power_equipment_summary(redfish_obj)
        redfish_utilities.print_power_equipment_summary(power_equipment)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
