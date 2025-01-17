#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Thermal Equipment

File : rf_thermal_equipment.py

Brief : This script uses the redfish_utilities module to manage thermal equipment
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
argget = argparse.ArgumentParser(description="A tool to manage thermal equipment")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
subparsers = argget.add_subparsers(dest="command")
list_argget = subparsers.add_parser("list", help="Displays a list of the available thermal equipment")
status_argget = subparsers.add_parser("status", help="Displays the status of an instance of thermal equipment")
status_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
status_argget.add_argument("--equipment", "-te", type=str, help="The identifier of the thermal equipment to get")
primary_info_argget = subparsers.add_parser(
    "primaryinfo", help="Displays the status of a primary coolant connector for an instance of thermal equipment"
)
primary_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
primary_info_argget.add_argument("--equipment", "-te", type=str, help="The identifier of the thermal equipment to get")
primary_info_argget.add_argument(
    "--primary", "-pr", type=str, help="The identifier of the primary coolant connector to get"
)
secondary_info_argget = subparsers.add_parser(
    "secondaryinfo", help="Displays the status of a secondary coolant connector for an instance of thermal equipment"
)
secondary_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
secondary_info_argget.add_argument(
    "--equipment", "-te", type=str, help="The identifier of the thermal equipment to get"
)
secondary_info_argget.add_argument(
    "--secondary", "-sec", type=str, help="The identifier of the secondary coolant connector to get"
)
pump_info_argget = subparsers.add_parser(
    "pumpinfo", help="Displays the status of a pump for an instance of thermal equipment"
)
pump_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
pump_info_argget.add_argument("--equipment", "-te", type=str, help="The identifier of the thermal equipment to get")
pump_info_argget.add_argument("--pump", "-pu", type=str, help="The identifier of the pump to get")
filter_info_argget = subparsers.add_parser(
    "filterinfo", help="Displays the status of a filter for an instance of thermal equipment"
)
filter_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
filter_info_argget.add_argument("--equipment", "-te", type=str, help="The identifier of the thermal equipment to get")
filter_info_argget.add_argument("--filter", "-fil", type=str, help="The identifier of the filter to get")
reservoir_info_argget = subparsers.add_parser(
    "reservoirinfo", help="Displays the status of a reservoir for an instance of thermal equipment"
)
reservoir_info_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
reservoir_info_argget.add_argument(
    "--equipment", "-te", type=str, help="The identifier of the thermal equipment to get"
)
reservoir_info_argget.add_argument("--reservoir", "-res", type=str, help="The identifier of the reservoir to get")
leak_detectors_argget = subparsers.add_parser(
    "leakdetectors", help="Displays the leak detector summary of an instance of thermal equipment"
)
leak_detectors_argget.add_argument(
    "--type",
    "-t",
    type=redfish_utilities.thermal_equipment_types,
    required=True,
    help="The type of thermal equipment to get",
    choices=redfish_utilities.thermal_equipment_types,
)
leak_detectors_argget.add_argument(
    "--equipment", "-te", type=str, help="The identifier of the thermal equipment to get"
)
args = argget.parse_args()

if args.debug:
    log_file = "rf_thermal_equipment-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_thermal_equipment Trace")

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
        thermal_equipment = redfish_utilities.get_thermal_equipment(
            redfish_obj,
            args.type,
            args.equipment,
            get_metrics=True,
            get_primary_connectors=True,
            get_secondary_connectors=True,
            get_pumps=True,
            get_filters=True,
            get_reservoirs=True,
            get_leak_detection=True,
        )
        redfish_utilities.print_thermal_equipment(thermal_equipment)
        component_types = [
            redfish_utilities.thermal_equipment_component_types.PRIMARY_CONNECTOR,
            redfish_utilities.thermal_equipment_component_types.SECONDARY_CONNECTOR,
            redfish_utilities.thermal_equipment_component_types.PUMP,
            redfish_utilities.thermal_equipment_component_types.FILTER,
            redfish_utilities.thermal_equipment_component_types.RESERVOIR,
        ]
        for component_type in component_types:
            redfish_utilities.print_thermal_equipment_component_summary(thermal_equipment, component_type, False)
    elif args.command == "primaryinfo":
        primary = redfish_utilities.get_thermal_equipment_component(
            redfish_obj,
            args.type,
            redfish_utilities.thermal_equipment_component_types.PRIMARY_CONNECTOR,
            args.equipment,
            args.primary,
        )
        redfish_utilities.print_thermal_equipment_component(primary)
    elif args.command == "secondaryinfo":
        secondary = redfish_utilities.get_thermal_equipment_component(
            redfish_obj,
            args.type,
            redfish_utilities.thermal_equipment_component_types.SECONDARY_CONNECTOR,
            args.equipment,
            args.secondary,
        )
        redfish_utilities.print_thermal_equipment_component(secondary)
    elif args.command == "pumpinfo":
        pump = redfish_utilities.get_thermal_equipment_component(
            redfish_obj, args.type, redfish_utilities.thermal_equipment_component_types.PUMP, args.equipment, args.pump
        )
        redfish_utilities.print_thermal_equipment_component(pump)
    elif args.command == "filterinfo":
        filter = redfish_utilities.get_thermal_equipment_component(
            redfish_obj,
            args.type,
            redfish_utilities.thermal_equipment_component_types.FILTER,
            args.equipment,
            args.filter,
        )
        redfish_utilities.print_thermal_equipment_component(filter)
    elif args.command == "reservoirinfo":
        reservoir = redfish_utilities.get_thermal_equipment_component(
            redfish_obj,
            args.type,
            redfish_utilities.thermal_equipment_component_types.RESERVOIR,
            args.equipment,
            args.reservoir,
        )
        redfish_utilities.print_thermal_equipment_component(reservoir)
    elif args.command == "leakdetectors":
        thermal_equipment = redfish_utilities.get_thermal_equipment(
            redfish_obj,
            args.type,
            args.equipment,
            get_leak_detection=True,
            get_leak_detectors=True,
        )
        redfish_utilities.print_thermal_equipment_leak_detector_summary(thermal_equipment, True)
    else:
        thermal_equipment = redfish_utilities.get_thermal_equipment_summary(redfish_obj)
        redfish_utilities.print_thermal_equipment_summary(thermal_equipment)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
