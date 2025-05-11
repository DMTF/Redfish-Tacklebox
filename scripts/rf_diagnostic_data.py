#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Diagnostic Data

File : rf_diagnostic_data.py

Brief : This script uses the redfish_utilities module to collect diagnostic data from a log service
"""

import argparse

# import logging
import os
import redfish
import redfish_utilities
import traceback
import sys
from redfish.messages import RedfishPasswordChangeRequiredError
from redfish_utilities.arguments import create_parent_parser, validate_args
from redfish_utilities.logger import setup_logger

# Get the input arguments
description = "A tool to collect diagnostic data from a log service on a Redfish service"
parent_parser = create_parent_parser(description=description, auth=True, rhost=True)
argget = argparse.ArgumentParser(parents=[parent_parser])

argget.add_argument(
    "--manager", "-m", type=str, nargs="?", default=False, help="The ID of the manager containing the log service"
)
argget.add_argument(
    "--system", "-s", type=str, nargs="?", default=False, help="The ID of the system containing the log service"
)
argget.add_argument(
    "--chassis", "-c", type=str, nargs="?", default=False, help="The ID of the chassis containing the log service"
)
argget.add_argument("--log", "-l", type=str, help="The ID of the log service")

argget.add_argument(
    "--type",
    "-type",
    type=redfish_utilities.diagnostic_data_types,
    help="The type of diagnostic data to collect; defaults to 'Manager' if not specified",
    choices=redfish_utilities.diagnostic_data_types,
    default=redfish_utilities.diagnostic_data_types.MANAGER,
)
argget.add_argument(
    "--oemtype",
    "-oemtype",
    type=str,
    help="The OEM-specific type of diagnostic data to collect; this option should only be used if the requested type is 'OEM'",
)
argget.add_argument(
    "--directory",
    "-d",
    type=str,
    help="The directory to save the diagnostic data; defaults to the current directory if not specified",
    default=".",
)

args = argget.parse_args()
validate_args(args)
logger = setup_logger(
    file_log=args.log_to_file, stream_log=args.log_to_console, log_level=args.log_level, file_name=__file__
)


# Determine the target log service based on the inputs
# Effectively if the user gives multiple targets, some will be ignored
container_type = redfish_utilities.log_container.MANAGER
container_id = None
if args.manager is not False:
    container_type = redfish_utilities.log_container.MANAGER
    container_id = args.manager
elif args.system is not False:
    container_type = redfish_utilities.log_container.SYSTEM
    container_id = args.system
elif args.chassis is not False:
    container_type = redfish_utilities.log_container.CHASSIS
    container_id = args.chassis

if args.debug:
    log_file = "rf_diagnostic_data-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_diagnostic_data Trace")

# Set up the Redfish object
redfish_obj = None
try:
    if args.session_token:
        sessionkey = str.encode(args.session_token)
        redfish_obj = redfish.redfish_client(base_url=args.rhost, sessionkey=sessionkey, timeout=15, max_retry=3)
    else:
        redfish_obj = redfish.redfish_client(
            base_url=args.rhost, username=args.user, password=args.password, timeout=15, max_retry=3
        )
        # Don't need to login if we're using a session key
        redfish_obj.login(auth="session")
except RedfishPasswordChangeRequiredError:
    redfish_utilities.print_password_change_required_and_logout(redfish_obj, args)
    sys.exit(1)
except Exception:
    raise

exit_code = 0
try:
    logger.info("Collecting diagnostic data...")
    response = redfish_utilities.collect_diagnostic_data(
        redfish_obj, container_type, container_id, args.log, args.type, args.oemtype
    )
    response = redfish_utilities.poll_task_monitor(redfish_obj, response)
    filename, data = redfish_utilities.download_diagnostic_data(redfish_obj, response)

    # Save the file
    if not os.path.isdir(args.directory):
        os.makedirs(args.directory)
    path = os.path.join(args.directory, filename)
    name_parts = filename.split(".", 1)
    file_check = 0
    if len(name_parts) == 1:
        name_parts.append("")
    while os.path.isfile(path):
        # If the file already exists, build a new file name with a counter
        file_check = file_check + 1
        filename = "{}({}).{}".format(name_parts[0], file_check, name_parts[1])
        path = os.path.join(args.directory, filename)
    with open(path, "wb") as file:
        file.write(data)
    logger.info("Saved diagnostic data to '{}'".format(path))
except Exception as e:
    logger.debug("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    logger.info(e)
finally:
    # Log out
    if not args.session_token:
        redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
