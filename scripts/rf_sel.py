#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish SEL

File : rf_sel.py

Brief : This script uses the redfish_utilities module to manage the SEL
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
argget = argparse.ArgumentParser(description="A tool to manage the SEL on a Redfish service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument(
    "--details", "-details", action="store_true", help="Indicates details to be shown for each log entry"
)
argget.add_argument("--clear", "-clear", action="store_true", help="Indicates if the log should be cleared")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
args = argget.parse_args()

if args.debug:
    log_file = "rf_sel-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_sel Trace")

# Set up the Redfish object
redfish_obj = None
try:
    redfish_obj = redfish.redfish_client(
        base_url=args.rhost, username=args.user, password=args.password, timeout=30, max_retry=3
    )
    redfish_obj.login(auth="session")
except RedfishPasswordChangeRequiredError:
    redfish_utilities.print_password_change_required_and_logout(redfish_obj, args)
    sys.exit(1)
except Exception:
    raise

exit_code = 0
try:
    # Find the SEL
    match = False
    for container_type in [redfish_utilities.log_container.MANAGER, redfish_utilities.log_container.SYSTEM]:
        if container_type == redfish_utilities.log_container.MANAGER:
            container_ids = redfish_utilities.get_manager_ids(redfish_obj)
        else:
            container_ids = redfish_utilities.get_system_ids(redfish_obj)
        for container in container_ids:
            try:
                container, log_service_ids = redfish_utilities.get_log_service_ids(
                    redfish_obj, container_type=container_type, container_id=container
                )
                for log_service in log_service_ids:
                    log_service_resp = redfish_utilities.get_log_service(
                        redfish_obj, container_type=container_type, container_id=container, log_service_id=log_service
                    )
                    if (
                        log_service_resp.dict.get("LogEntryType") == "SEL"
                        or log_service_resp.dict["Id"].upper() == "SEL"
                    ):
                        match = True
                        break
            except Exception:
                pass
            if match:
                break
        if match:
            break
    if match:
        # Either clear the logs or get/print the logs
        if args.clear:
            # Clear log was requested
            print("Clearing the SEL...")
            response = redfish_utilities.clear_log_entries(redfish_obj, log_service=log_service_resp)
            response = redfish_utilities.poll_task_monitor(redfish_obj, response)
            redfish_utilities.verify_response(response)
        else:
            # Print log was requested
            log_entries = redfish_utilities.get_log_entries(redfish_obj, log_service=log_service_resp)
            try:
                from signal import signal, SIGPIPE, SIG_DFL

                signal(SIGPIPE, SIG_DFL)
            except Exception:
                # Windows does not support SIGPIPE; no need to modify the handling
                pass
            redfish_utilities.print_log_entries(log_entries, args.details)
    else:
        print("No SEL found")
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
