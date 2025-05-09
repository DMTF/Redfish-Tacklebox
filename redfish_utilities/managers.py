#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Managers Module

File : managers.py

Brief : This file contains the definitions and functionalities for interacting
        with the managers collection for a given Redfish service
"""

import sys
from .collections import get_collection_ids
from .messages import verify_response
from .resets import reset_types
from .resets import reset_to_defaults_types


class RedfishManagerNotFoundError(Exception):
    """
    Raised when a matching manager cannot be found
    """

    pass


class RedfishManagerNetworkProtocolNotFoundError(Exception):
    """
    Raised when a matching manager does not contain network protocol information
    """

    pass


class RedfishManagerEthIntNotFoundError(Exception):
    """
    Raised when a matching Ethernet interface cannot be found
    """

    pass


class RedfishManagerResetNotFoundError(Exception):
    """
    Raised when the Reset action cannot be found
    """

    pass


class RedfishManagerResetToDefaultsNotFoundError(Exception):
    """
    Raised when the ResetToDefaults action cannot be found
    """

    pass


def get_manager_ids(context):
    """
    Finds the manager collection and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list of identifiers of the members of the manager collection
    """

    # Get the service root to find the manager collection
    service_root = context.get("/redfish/v1/")
    if "Managers" not in service_root.dict:
        # No manager collection
        raise RedfishManagerNotFoundError("The service does not contain a manager collection")

    # Get the manager collection and iterate through its collection
    return get_collection_ids(context, service_root.dict["Managers"]["@odata.id"])


def get_manager(context, manager_id=None):
    """
    Finds a manager matching the given identifier and returns its resource

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager

    Returns:
        The manager resource
    """

    manager_uri_pattern = "/redfish/v1/Managers/{}"
    avail_managers = None

    # If given an identifier, get the manager directly
    if manager_id is not None:
        manager = context.get(manager_uri_pattern.format(manager_id))
    # No identifier given; see if there's exactly one member
    else:
        avail_managers = get_manager_ids(context)
        if len(avail_managers) == 1:
            manager = context.get(manager_uri_pattern.format(avail_managers[0]))
        else:
            raise RedfishManagerNotFoundError(
                "The service does not contain exactly one manager; a target manager needs to be specified: {}".format(
                    ", ".join(avail_managers)
                )
            )

    # Check the response and return the manager if the response is good
    if manager.status == 404:
        if avail_managers is None:
            avail_managers = get_manager_ids(context)
        raise RedfishManagerNotFoundError(
            "The service does not contain a manager called {}; valid managers: {}".format(
                manager_id, ", ".join(avail_managers)
            )
        )
    verify_response(manager)
    return manager


def set_manager(context, manager_id=None, date_time=None, date_time_offset=None):
    """
    Finds a manager matching the given identifier and sets one or more properties

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        date_time: The date-time value to set
        date_time_offset: The date-time offset value to set

    Returns:
        The response of the PATCH
    """

    # Locate the manager
    manager = get_manager(context, manager_id)

    # Build the payload
    payload = {}
    if date_time is not None:
        payload["DateTime"] = date_time
    if date_time_offset is not None:
        payload["DateTimeLocalOffset"] = date_time_offset

    # Update the manager
    headers = None
    etag = manager.getheader("ETag")
    if etag is not None:
        headers = {"If-Match": etag}
    response = context.patch(manager.dict["@odata.id"], body=payload, headers=headers)
    verify_response(response)
    return response


def print_manager(manager):
    """
    Prints the manager info

    Args:
        manager: The manager info to print
    """

    manager_line_format = "  {}: {}"
    manager_properties = [
        "Status",
        "ManagerType",
        "PowerState",
        "FirmwareVersion",
        "DateTime",
        "DateTimeLocalOffset",
        "LastResetTime",
        "UUID",
        "ServiceEntryPointUUID",
        "Manufacturer",
        "Model",
        "PartNumber",
        "SparePartNumber",
        "SerialNumber",
    ]
    print("Manager {} Info".format(manager.dict["Id"]))
    for property in manager_properties:
        if property in manager.dict:
            prop_val = manager.dict[property]
            if isinstance(prop_val, list):
                prop_val = ", ".join([i for i in prop_val if i is not None])
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format(prop_val.get("State", "N/A"), prop_val.get("Health", "N/A"))
            print(manager_line_format.format(property, prop_val))
    print("")


def get_manager_reset_info(context, manager_id=None, manager=None):
    """
    Finds a manager matching the given ID and returns its reset info

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        manager: Existing manager resource to inspect for reset info

    Returns:
        The URI of the Reset action
        A list of parameter requirements from the action info
    """

    if manager is None:
        manager = get_manager(context, manager_id)

    # Check that there is a Reset action
    if "Actions" not in manager.dict:
        raise RedfishManagerResetNotFoundError(
            "Manager {} does not support the Reset action".format(manager.dict["Id"])
        )
    if "#Manager.Reset" not in manager.dict["Actions"]:
        raise RedfishManagerResetNotFoundError(
            "Manager {} does not support the Reset action".format(manager.dict["Id"])
        )

    # Extract the info about the Reset action
    reset_action = manager.dict["Actions"]["#Manager.Reset"]
    reset_uri = reset_action["target"]

    if "@Redfish.ActionInfo" not in reset_action:
        # No action info; need to build this manually based on other annotations

        # Default parameter requirements
        reset_parameters = [
            {"Name": "ResetType", "Required": False, "DataType": "String", "AllowableValues": reset_types}
        ]

        # Get the AllowableValues from annotations
        for param in reset_parameters:
            if param["Name"] + "@Redfish.AllowableValues" in reset_action:
                param["AllowableValues"] = reset_action[param["Name"] + "@Redfish.AllowableValues"]
    else:
        # Get the action info and its parameter listing
        action_info = context.get(reset_action["@Redfish.ActionInfo"])
        reset_parameters = action_info.dict["Parameters"]

    return reset_uri, reset_parameters


def manager_reset(context, manager_id=None, reset_type=None):
    """
    Finds a manager matching the given ID and performs a reset

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        reset_type: The type of reset to perform; if None, perform one of the common resets

    Returns:
        The response of the action
    """

    # Check that the values themselves are supported by the schema
    reset_type_values = reset_types
    if reset_type is not None:
        if reset_type not in reset_type_values:
            raise ValueError("{} is not an allowable reset type ({})".format(reset_type, ", ".join(reset_type_values)))

    # Locate the reset action
    reset_uri, reset_parameters = get_manager_reset_info(context, manager_id)

    # Build the payload
    if reset_type is None:
        for param in reset_parameters:
            if param["Name"] == "ResetType":
                if "GracefulRestart" in param["AllowableValues"]:
                    reset_type = "GracefulRestart"
                elif "ForceRestart" in param["AllowableValues"]:
                    reset_type = "ForceRestart"
                elif "PowerCycle" in param["AllowableValues"]:
                    reset_type = "PowerCycle"

    payload = {}
    if reset_type is not None:
        payload["ResetType"] = reset_type

    # Reset the manager
    response = context.post(reset_uri, body=payload)
    try:
        verify_response(response)
    except Exception as e:
        additional_message = ""
        if response.status == 400:
            # Append the list of valid reset types to 400 Bad Request responses
            additional_message = "\nNo supported reset types listed"
            for param in reset_parameters:
                if param["Name"] == "ResetType" and "AllowableValues" in param:
                    additional_message = "\nSupported reset types: {}".format(", ".join(param["AllowableValues"]))
        raise type(e)(str(e) + additional_message).with_traceback(sys.exc_info()[2])
    return response


def get_manager_reset_to_defaults_info(context, manager_id=None, manager=None):
    """
    Finds a manager matching the given ID and returns its reset-to-defaults info

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        manager: Existing manager resource to inspect for reset info

    Returns:
        The URI of the Reset action
        A list of parameter requirements from the action info
    """

    if manager is None:
        manager = get_manager(context, manager_id)

    # Check that there is a Reset action
    if "Actions" not in manager.dict:
        raise RedfishManagerResetToDefaultsNotFoundError(
            "Manager {} does not support the ResetToDefaults action".format(manager.dict["Id"])
        )
    if "#Manager.ResetToDefaults" not in manager.dict["Actions"]:
        raise RedfishManagerResetToDefaultsNotFoundError(
            "Manager {} does not support the ResetToDefaults action".format(manager.dict["Id"])
        )

    # Extract the info about the ResetToDefaults action
    reset_action = manager.dict["Actions"]["#Manager.ResetToDefaults"]
    reset_uri = reset_action["target"]

    if "@Redfish.ActionInfo" not in reset_action:
        # No action info; need to build this manually based on other annotations

        # Default parameter requirements
        reset_parameters = [
            {"Name": "ResetType", "Required": True, "DataType": "String", "AllowableValues": reset_to_defaults_types}
        ]

        # Get the AllowableValues from annotations
        for param in reset_parameters:
            if param["Name"] + "@Redfish.AllowableValues" in reset_action:
                param["AllowableValues"] = reset_action[param["Name"] + "@Redfish.AllowableValues"]
    else:
        # Get the action info and its parameter listing
        action_info = context.get(reset_action["@Redfish.ActionInfo"])
        reset_parameters = action_info.dict["Parameters"]

    return reset_uri, reset_parameters


def manager_reset_to_defaults(context, manager_id=None, reset_type=None):
    """
    Finds a manager matching the given ID and performs a reset-to-defaults

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        reset_type: The type of reset to perform; if None, perform one of the common resets

    Returns:
        The response of the action
    """

    # Check that the values themselves are supported by the schema
    reset_to_default_type_values = reset_to_defaults_types
    if reset_type is not None:
        if reset_type not in reset_to_default_type_values:
            raise ValueError(
                "{} is not an allowable reset type ({})".format(reset_type, ", ".join(reset_to_default_type_values))
            )

    # Locate the reset action
    reset_uri, reset_parameters = get_manager_reset_to_defaults_info(context, manager_id)

    # Build the payload
    if reset_type is None:
        for param in reset_parameters:
            if param["Name"] == "ResetType":
                if "PreserveNetworkAndUsers" in param["AllowableValues"]:
                    reset_type = "PreserveNetworkAndUsers"
                elif "PreserveNetwork" in param["AllowableValues"]:
                    reset_type = "PreserveNetwork"
                elif "ResetAll" in param["AllowableValues"]:
                    reset_type = "ResetAll"

    payload = {}
    if reset_type is not None:
        payload["ResetType"] = reset_type

    # Reset the manager to defaults
    response = context.post(reset_uri, body=payload)
    try:
        verify_response(response)
    except Exception as e:
        additional_message = ""
        if response.status == 400:
            # Append the list of valid reset types to 400 Bad Request responses
            additional_message = "\nNo supported reset types listed"
            for param in reset_parameters:
                if param["Name"] == "ResetType" and "AllowableValues" in param:
                    additional_message = "\nSupported reset types: {}".format(", ".join(param["AllowableValues"]))
        raise type(e)(str(e) + additional_message).with_traceback(sys.exc_info()[2])
    return response


def get_manager_network_protocol(context, manager_id=None):
    """
    Finds the network protocol information for a manager and returns its resource

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager

    Returns:
        The ManagerNetworkProtocol resource
    """
    # Get the manager to find its network protocol information
    manager = get_manager(context, manager_id)
    if "NetworkProtocol" not in manager.dict:
        # No network protocol information
        raise RedfishManagerNetworkProtocolNotFoundError(
            "Manager {} does not contain network protocol information".format(manager.dict["Id"])
        )

    # Get the network protocol information
    response = context.get(manager.dict["NetworkProtocol"]["@odata.id"])
    verify_response(response)
    return response


def set_manager_network_protocol(context, manager_id=None, network_protocol=None):
    """
    Sets network protocol settings for a manager

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        network_protocol: The network protocol settings to apply

    Returns:
        The response of the PATCH
    """
    # Get the manager to find its network protocol information
    manager = get_manager(context, manager_id)
    if "NetworkProtocol" not in manager.dict:
        # No network protocol information
        raise RedfishManagerNetworkProtocolNotFoundError(
            "Manager {} does not contain network protocol information".format(manager.dict["Id"])
        )

    # Get the current network protocol information
    response = context.get(manager.dict["NetworkProtocol"]["@odata.id"])
    verify_response(response)
    headers = None
    etag = response.getheader("ETag")
    if etag is not None:
        headers = {"If-Match": etag}

    # Set the network protocol information
    if network_protocol is None:
        network_protocol = {}
    response = context.patch(manager.dict["NetworkProtocol"]["@odata.id"], body=network_protocol, headers=headers)
    verify_response(response)
    return response


def print_manager_network_protocol(network_protocol):
    """
    Prints the manager network protocol information

    Args:
        network_protocol: The manager network protocol information to print
    """

    network_protocol_properties = [
        "HTTP",
        "HTTPS",
        "SSDP",
        "SSH",
        "Telnet",
        "KVMIP",
        "NTP",
        "RDP",
        "RFB",
        "VirtualMedia",
        "IPMI",
        "SNMP",
        "DHCP",
        "DHCPv6",
    ]
    network_protocol_line_format = "  {:16s} | {:8s} | {:6s} | {}"
    print("Manager Network Protocol Info")
    print("")
    print(network_protocol_line_format.format("Protocol", "Enabled", "Port", "Other Settings"))

    for property in network_protocol_properties:
        if property in network_protocol.dict:
            other_str = ""
            if property == "SSDP":
                # For SSDP, extract the NOTIFY settings
                other_str = []
                if "NotifyIPv6Scope" in network_protocol.dict[property]:
                    other_str.append("NOTIFY IPv6 Scope: {}".format(network_protocol.dict[property]["NotifyIPv6Scope"]))
                if "NotifyTTL" in network_protocol.dict[property]:
                    other_str.append("NOTIFY TTL: {}".format(network_protocol.dict[property]["NotifyTTL"]))
                if "NotifyMulticastIntervalSeconds" in network_protocol.dict[property]:
                    other_str.append(
                        "NOTIFY ALIVE Interval: {}".format(
                            network_protocol.dict[property]["NotifyMulticastIntervalSeconds"]
                        )
                    )
                other_str = ", ".join(other_str)
            if property == "NTP":
                # For NTP, extract the servers; need to skip "empty" slots potentially
                if "NTPServers" in network_protocol.dict[property]:
                    other_str = "NTP Servers: " + ", ".join(
                        [i for i in network_protocol.dict[property]["NTPServers"] if i is not None]
                    )
            print(
                network_protocol_line_format.format(
                    property,
                    str(network_protocol.dict[property].get("ProtocolEnabled", "")),
                    str(network_protocol.dict[property].get("Port", "")),
                    other_str,
                )
            )


def get_manager_ethernet_interface_ids(context, manager_id=None):
    """
    Finds the Ethernet interface collection for a manager and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager

    Returns:
        A list of identifiers of the members of the Ethernet interface collection
    """

    # Get the manager to find its Ethernet interface collection
    manager = get_manager(context, manager_id)
    if "EthernetInterfaces" not in manager.dict:
        # No Ethernet interface collection
        raise RedfishManagerEthIntNotFoundError(
            "Manager {} does not contain an Ethernet interface collection".format(manager.dict["Id"])
        )

    # Get the Ethernet interface collection and iterate through its collection
    return get_collection_ids(context, manager.dict["EthernetInterfaces"]["@odata.id"])


def get_manager_ethernet_interface(context, manager_id=None, interface_id=None):
    """
    Finds an Ethernet interface for a manager matching the given identifiers and returns its resource

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        interface_id: The Ethernet interface to locate; if None, perform on the only Ethernet interface

    Returns:
        The EthernetInterface resource for the manager
    """

    interface_uri_pattern = "/redfish/v1/Managers/{}/EthernetInterfaces/{}"
    avail_interfaces = None

    # Get the manager identifier in order to build the full URI later
    if manager_id is None:
        manager = get_manager(context, None)
        manager_id = manager.dict["Id"]

    # If given an identifier, get the Ethernet interface directly
    if interface_id is not None:
        interface = context.get(interface_uri_pattern.format(manager_id, interface_id))
    # No identifier given; see if there's exactly one member
    else:
        avail_interfaces = get_manager_ethernet_interface_ids(context, manager_id)
        if len(avail_interfaces) == 1:
            interface = context.get(interface_uri_pattern.format(manager_id, avail_interfaces[0]))
        else:
            raise RedfishManagerEthIntNotFoundError(
                "Manager {} does not contain exactly one Ethernet interface; a target Ethernet interface needs to be specified: {}".format(
                    manager_id, ", ".join(avail_interfaces)
                )
            )

    # Check the response and return the Ethernet interface if the response is good
    if interface.status == 404:
        if avail_interfaces is None:
            avail_interfaces = get_manager_ethernet_interface_ids(context, manager_id)
        raise RedfishManagerEthIntNotFoundError(
            "Manager {} does not contain an Ethernet interface called {}; valid Ethernet interfaces: {}".format(
                manager_id, interface_id, ", ".join(avail_interfaces)
            )
        )
    verify_response(interface)
    return interface


def set_manager_ethernet_interface(
    context,
    manager_id=None,
    interface_id=None,
    vlan=None,
    ipv4_addresses=None,
    dhcpv4=None,
    ipv6_addresses=None,
    ipv6_gateways=None,
    dhcpv6=None,
):
    """
    Finds an Ethernet interface matching the given ID and updates specified properties

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        interface_id: The Ethernet interface to locate; if None, perform on the only interface
        vlan: An object containing new VLAN settings for the interface
        ipv4_addresses: An array of objects containing new IPv4 static addresses for the interface
        dhcpv4: An object containing new DHCPv4 settings for the interface
        ipv6_addresses: An array of objects containing new IPv6 static addresses for the interface
        ipv6_gateways: New IPv6 static gateways for the interface
        dhcpv6: An object containing new DHCPv6 settings for the interface

    Returns:
        The response of the PATCH
    """

    # Locate the interface
    interface = get_manager_ethernet_interface(context, manager_id, interface_id)

    # Update the interface based on the request parameters
    payload = {}
    if vlan is not None:
        payload["VLAN"] = vlan
    if ipv4_addresses is not None:
        if "IPv4StaticAddresses" in interface.dict:
            payload["IPv4StaticAddresses"] = ipv4_addresses
        else:
            # Older services manage static addresses through the "assigned addresses" property
            payload["IPv4Addresses"] = ipv4_addresses
    if dhcpv4 is not None:
        payload["DHCPv4"] = dhcpv4
    if ipv6_addresses is not None:
        payload["IPv6StaticAddresses"] = ipv6_addresses
    if ipv6_gateways is not None:
        payload["IPv6StaticDefaultGateways"] = ipv6_gateways
    if dhcpv6 is not None:
        payload["DHCPv6"] = dhcpv6
    headers = None
    etag = interface.getheader("ETag")
    if etag is not None:
        headers = {"If-Match": etag}
    response = context.patch(interface.dict["@odata.id"], body=payload, headers=headers)
    verify_response(response)
    return response


def print_manager_ethernet_interface(interface):
    """
    Prints the Ethernet interface info

    Args:
        interface: The Ethernet interface info to print
    """

    interface_line_format = "  {}: {}"
    interface_properties = [
        "Status",
        "InterfaceEnabled",
        "LinkStatus",
        "MACAddress",
        "PermanentMACAddress",
        "SpeedMbps",
        "AutoNeg",
        "FullDuplex",
        "MTUSize",
        "HostName",
        "FQDN",
        "NameServers",
        "StaticNameServers",
    ]
    print("Ethernet Interface {} Info".format(interface.dict["Id"]))
    for property in interface_properties:
        if property in interface.dict:
            prop_val = interface.dict[property]
            if isinstance(prop_val, list):
                prop_val = ", ".join([i for i in prop_val if i is not None])
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format(prop_val.get("State", "N/A"), prop_val.get("Health", "N/A"))
            print(interface_line_format.format(property, prop_val))
    print("")

    if "VLAN" in interface.dict:
        print("  VLAN Info")
        print("    Enabled: {}".format(interface.dict["VLAN"].get("VLANEnable", False)))
        print("    ID: {}".format(interface.dict["VLAN"].get("VLANId", "N/A")))
        print("    Priority: {}".format(interface.dict["VLAN"].get("VLANPriority", "N/A")))
        print("")

    print("  IPv4 Info")
    if "DHCPv4" in interface.dict:
        print("    DHCP Enabled: {}".format(interface.dict["DHCPv4"]["DHCPEnabled"]))
    if "IPv4Addresses" in interface.dict:
        print("    Assigned Addresses")
        for i, address in enumerate(interface.dict["IPv4Addresses"]):
            if address is None:
                print("      Empty")
            elif i == 0:
                print(
                    "      {}: {}, {}, {}".format(
                        address.get("Address", "N/A"),
                        address.get("SubnetMask", "N/A"),
                        address.get("Gateway", "N/A"),
                        address.get("AddressOrigin", "N/A"),
                    )
                )
            else:
                print(
                    "      {}: {}, {}".format(
                        address.get("Address", "N/A"),
                        address.get("SubnetMask", "N/A"),
                        address.get("AddressOrigin", "N/A"),
                    )
                )
    if "IPv4StaticAddresses" in interface.dict:
        print("    Static Addresses")
        for i, address in enumerate(interface.dict["IPv4StaticAddresses"]):
            if address is None:
                print("       Empty")
            elif i == 0:
                print(
                    "      {}: {}, {}".format(
                        address.get("Address", "N/A"), address.get("SubnetMask", "N/A"), address.get("Gateway", "N/A")
                    )
                )
            else:
                print("      {}: {}".format(address["Address"], address["SubnetMask"]))
    print("")

    print("  IPv6 Info")
    if "DHCPv6" in interface.dict:
        print("    DHCP Mode: {}".format(interface.dict["DHCPv6"]["OperatingMode"]))
    if "IPv6Addresses" in interface.dict:
        print("    Assigned Addresses")
        for address in interface.dict["IPv6Addresses"]:
            print(
                "      {}/{}: {}, {}".format(
                    address.get("Address", "N/A"),
                    address.get("PrefixLength", "N/A"),
                    address.get("AddressOrigin", "N/A"),
                    address.get("AddressState", "N/A"),
                )
            )
    if "IPv6StaticAddresses" in interface.dict:
        print("    Static Addresses")
        for address in interface.dict["IPv6StaticAddresses"]:
            if address is None:
                print("      Empty")
            else:
                print("      {}/{}".format(address.get("Address", "N/A"), address.get("PrefixLength", "N/A")))
    if "IPv6StaticDefaultGateways" in interface.dict:
        print("    Static Default Gateways")
        for address in interface.dict["IPv6StaticDefaultGateways"]:
            if address is None:
                print("      Empty")
            else:
                print("      {}/{}".format(address.get("Address", "N/A"), address.get("PrefixLength", "N/A")))
    if "IPv6DefaultGateway" in interface.dict:
        print("    Default Gateway: {}".format(interface.dict["IPv6DefaultGateway"]))
    if "IPv6AddressPolicyTable" in interface.dict:
        print("    Address Policy Table")
        for policy in interface.dict["IPv6AddressPolicyTable"]:
            if policy is None:
                print("      Empty")
            else:
                print(
                    "      Prefix: {}, Prec: {}, Label: {}".format(
                        policy.get("Prefix", "N/A"), policy.get("Precedence", "N/A"), policy.get("Label", "N/A")
                    )
                )
    print("")
