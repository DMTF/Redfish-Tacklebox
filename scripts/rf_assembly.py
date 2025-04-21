#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Assembly

File : rf_assembly.py

Brief : This script uses the redfish_utilities module to manage assemblies
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
argget = argparse.ArgumentParser(description="A tool to manage assemblies on a Redfish service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--assembly", "-a", type=str, required=True, help="The URI of the target assembly")
argget.add_argument("--index", "-i", type=int, help="The target assembly index")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
subparsers = argget.add_subparsers(dest="command")
info_argget = subparsers.add_parser("info", help="Displays information about the an assembly")
download_argget = subparsers.add_parser("download", help="Downloads assembly data to a file")
download_argget.add_argument(
    "--file", "-f", type=str, required=True, help="The file, and optional path, to save the assembly data"
)
upload_argget = subparsers.add_parser("upload", help="Uploads assembly data from a file")
upload_argget.add_argument(
    "--file", "-f", type=str, required=True, help="The file, and optional path, containing the assembly data to upload"
)
args = argget.parse_args()

if args.index and args.index < 0:
    print("rf_assembly.py: error: the assembly index cannot be negative")
    sys.exit(1)

if args.debug:
    log_file = "rf_assembly-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_assembly Trace")

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
    assembly_info = redfish_utilities.get_assembly(redfish_obj, args.assembly)
    if args.command == "download":
        print("Saving data to '{}'...".format(args.file))
        redfish_utilities.download_assembly(redfish_obj, assembly_info, args.file, args.index)
    elif args.command == "upload":
        print("Writing data from '{}'...".format(args.file))
        redfish_utilities.upload_assembly(redfish_obj, assembly_info, args.file, args.index)
    else:
        redfish_utilities.print_assembly(assembly_info, args.index)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
