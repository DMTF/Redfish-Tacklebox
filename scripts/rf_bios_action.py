#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish BIOS Action

File : rf_bios_action.py

Brief : This script uses the redfish_utilities module to load default or change password of a system
"""

import argparse
import redfish
import redfish_utilities

# Get the input arguments
argget = argparse.ArgumentParser(description="A tool to manager BIOS settings for a system")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--system", "-s", type=str, help="The ID of the system to manage (default = the only system)")
argget.add_argument("--resetbios", "-rb", action="store_true", help="To load BIOS default")
argget.add_argument("--changepassword", "-cp", type=str, nargs='*', help="To change BIOS password. Followed by "
                                                                         "password name, old password and new password")
args = argget.parse_args()

if not args.resetbios and not args.changepassword:
    print('Need at least one action')
    exit(0)

# Set up the Redfish object
redfish_obj = redfish.redfish_client(base_url=args.rhost, username=args.user, password=args.password)
redfish_obj.login(auth="session")

try:
    # Try to load BIOS default
    if args.resetbios:
        redfish_utilities.reset_system_bios(redfish_obj, args.system)

    # Try to change BIOS password
    if args.changepassword:
        redfish_utilities.change_bios_password(redfish_obj, args.changepassword, args.system)

    print('Operation successes, please reboot to take effect')
finally:
    # Log out
    redfish_obj.logout()
