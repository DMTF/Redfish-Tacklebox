#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Manager Configuration

File : rf_manager_config.py

Brief : This script uses the redfish_utilities module to manage managers
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
argget = argparse.ArgumentParser(description="A tool to manage managers in a service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--manager", "-m", type=str, help="The ID of the manager to target")
argget.add_argument("--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions")
subparsers = argget.add_subparsers(dest="command")
info_argget = subparsers.add_parser("info", help="Displays information about a manager")
reset_argget = subparsers.add_parser("reset", help="Resets a manager")
reset_argget.add_argument(
    "--type", "-t", type=str, help="The type of power/reset operation to perform", choices=redfish_utilities.reset_types
)
reset_argget.add_argument(
    "--info", "-info", action="store_true", help="Indicates if reset information should be reported"
)
getnet_argget = subparsers.add_parser("getnet", help="Displays information about an Ethernet interface")
getnet_argget.add_argument("--id", "-i", type=str, help="The identifier of the Ethernet interface to display")
setnet_argget = subparsers.add_parser("setnet", help="Configures an Ethernet interface")
setnet_argget.add_argument("--id", "-i", type=str, help="The identifier of the Ethernet interface to configure")
setnet_argget.add_argument("--ipv4address", "-ipv4address", type=str, help="The static IPv4 address to set")
setnet_argget.add_argument("--ipv4netmask", "-ipv4netmask", type=str, help="The static IPv4 subnet mask to set")
setnet_argget.add_argument("--ipv4gateway", "-ipv4gateway", type=str, help="The static IPv4 gateway to set")
setnet_argget.add_argument(
    "--dhcpv4", "-dhcpv4", type=str, help="The DHCPv4 configuration to set", choices=["On", "Off"]
)
setnet_argget.add_argument(
    "--ipv6addresses", "-ipv6addresses", type=str, nargs="+", help="The static IPv6 addresses to set with prefix length"
)
setnet_argget.add_argument(
    "--ipv6gateways",
    "-ipv6gateways",
    type=str,
    nargs="+",
    help="The static IPv6 default gateways to set with prefix length",
)
setnet_argget.add_argument(
    "--dhcpv6",
    "-dhcpv6",
    type=str,
    help="The DHCPv6 configuration to set",
    choices=["Stateful", "Stateless", "Disabled", "Enabled"],
)
setnet_argget.add_argument(
    "--vlan", "-vlan", type=str, help="The VLAN enabled configuration to set", choices=["On", "Off"]
)
setnet_argget.add_argument("--vlanid", "-vlanid", type=int, help="The VLAN ID to set")
setnet_argget.add_argument("--vlanpriority", "-vlanpriority", type=int, help="The VLAN priority to set")
reset_to_defaults_argget = subparsers.add_parser("resettodefaults", help="Resets a manager to default settings")
reset_to_defaults_argget.add_argument(
    "--type",
    "-t",
    type=str,
    help="The type of reset-to-defaults operation to perform",
    choices=redfish_utilities.reset_to_defaults_types,
)
reset_to_defaults_argget.add_argument(
    "--info", "-info", action="store_true", help="Indicates if reset-to-defaults information should be reported"
)
set_time_argget = subparsers.add_parser("settime", help="Sets the date-time on a manager")
set_time_argget.add_argument("--datetime", "-dt", type=str, help="The date-time value to set")
set_time_argget.add_argument("--offset", "-o", type=str, help="The date-time offset value to set")
getprotocol_argget = subparsers.add_parser("getprotocol", help="Displays network protocol information about a manager")
setprotocol_argget = subparsers.add_parser("setprotocol", help="Configures network protocol settings on a manager")
setprotocol_argget.add_argument("--protocol", "-prot", type=str, required=True, help="The protocol to set")
setprotocol_argget.add_argument("--enable", "-en", action="store_true", help="Enable the selected protocol")
setprotocol_argget.add_argument("--disable", "-dis", action="store_true", help="Disable the selected protocol")
setprotocol_argget.add_argument("--port", "-port", type=int, help="The port number to assign the protocol")
args = argget.parse_args()

if args.debug:
    log_file = "rf_manager_config-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger(log_file, log_format, logging.DEBUG)
    logger.info("rf_manager_config Trace")

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
    if args.command == "reset":
        if args.info:
            reset_uri, reset_parameters = redfish_utilities.get_manager_reset_info(redfish_obj, args.manager)
            printed_reset_types = False
            for param in reset_parameters:
                if param["Name"] == "ResetType" and "AllowableValues" in param:
                    print("Supported reset types: {}".format(", ".join(param["AllowableValues"])))
                    printed_reset_types = True
            if not printed_reset_types:
                print("No reset information found")
        else:
            print("Resetting the manager...")
            response = redfish_utilities.manager_reset(redfish_obj, args.manager, args.type)
            response = redfish_utilities.poll_task_monitor(redfish_obj, response)
            redfish_utilities.verify_response(response)
    elif args.command == "resettodefaults":
        if args.info:
            reset_uri, reset_parameters = redfish_utilities.get_manager_reset_to_defaults_info(
                redfish_obj, args.manager
            )
            printed_reset_types = False
            for param in reset_parameters:
                if param["Name"] == "ResetType" and "AllowableValues" in param:
                    print("Supported reset types: {}".format(", ".join(param["AllowableValues"])))
                    printed_reset_types = True
            if not printed_reset_types:
                print("No reset information found")
        else:
            print("Resetting the manager to defaults...")
            response = redfish_utilities.manager_reset_to_defaults(redfish_obj, args.manager, args.type)
            response = redfish_utilities.poll_task_monitor(redfish_obj, response)
            redfish_utilities.verify_response(response)
    elif args.command == "settime":
        redfish_utilities.set_manager(redfish_obj, args.manager, args.datetime, args.offset)
    elif args.command == "getnet":
        interface = redfish_utilities.get_manager_ethernet_interface(redfish_obj, args.manager, args.id)
        redfish_utilities.print_manager_ethernet_interface(interface)
    elif args.command == "setnet":
        vlan = {}
        if args.vlan == "On":
            vlan["VLANEnable"] = True
        elif args.vlan == "Off":
            vlan["VLANEnable"] = False
        if args.vlanid is not None:
            vlan["VLANId"] = args.vlanid
        if args.vlanpriority is not None:
            vlan["VLANPriority"] = args.vlanpriority
        if len(vlan) == 0:
            vlan = None
        ipv4_addresses = [{}]
        if args.ipv4address is not None:
            ipv4_addresses[0]["Address"] = args.ipv4address
        if args.ipv4netmask is not None:
            ipv4_addresses[0]["SubnetMask"] = args.ipv4netmask
        if args.ipv4gateway is not None:
            ipv4_addresses[0]["Gateway"] = args.ipv4gateway
        if len(ipv4_addresses[0]) == 0:
            ipv4_addresses = None
        dhcpv4 = None
        if args.dhcpv4 == "On":
            dhcpv4 = {"DHCPEnabled": True}
        elif args.dhcpv4 == "Off":
            dhcpv4 = {"DHCPEnabled": False}
        dhcpv6 = None
        ipv6_addresses = None
        if args.ipv6addresses is not None:
            ipv6_addresses = []
            for address in args.ipv6addresses:
                if address == "None":
                    ipv6_addresses.append(None)
                elif address == "{}":
                    ipv6_addresses.append({})
                else:
                    ipv6_addresses.append(
                        {"Address": address.split("/")[0], "PrefixLength": int(address.split("/")[1])}
                    )
        ipv6_gateways = None
        if args.ipv6gateways is not None:
            ipv6_gateways = []
            for address in args.ipv6gateways:
                if address == "None":
                    ipv6_gateways.append(None)
                elif address == "{}":
                    ipv6_gateways.append({})
                else:
                    ipv6_gateways.append({"Address": address.split("/")[0], "PrefixLength": int(address.split("/")[1])})
        if args.dhcpv6 is not None:
            dhcpv6 = {"OperatingMode": args.dhcpv6}
        redfish_utilities.set_manager_ethernet_interface(
            redfish_obj, args.manager, args.id, vlan, ipv4_addresses, dhcpv4, ipv6_addresses, ipv6_gateways, dhcpv6
        )
    elif args.command == "getprotocol":
        network_protocol = redfish_utilities.get_manager_network_protocol(redfish_obj, args.manager)
        redfish_utilities.print_manager_network_protocol(network_protocol)
    elif args.command == "setprotocol":
        network_protocol_setting = {args.protocol: {}}
        if args.enable:
            network_protocol_setting[args.protocol]["ProtocolEnabled"] = True
        elif args.disable:
            network_protocol_setting[args.protocol]["ProtocolEnabled"] = False
        if args.port:
            network_protocol_setting[args.protocol]["Port"] = args.port
        print("Configuring {}...".format(args.protocol))
        redfish_utilities.set_manager_network_protocol(redfish_obj, args.manager, network_protocol_setting)
    else:
        manager = redfish_utilities.get_manager(redfish_obj, args.manager)
        redfish_utilities.print_manager(manager)
except Exception as e:
    if args.debug:
        logger.error("Caught exception:\n\n{}\n".format(traceback.format_exc()))
    exit_code = 1
    print(e)
finally:
    # Log out
    redfish_utilities.logout(redfish_obj)
sys.exit(exit_code)
