#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Managers Module

File : managers.py

Brief : This file contains the definitions and functionalities for interacting
        with the managers collection for a given Redfish service
"""

from .messages import verify_response
from .resets import reset_types

class RedfishManagerNotFoundError( Exception ):
    """
    Raised when a matching manager cannot be found
    """
    pass

class RedfishManagerEthIntNotFoundError( Exception ):
    """
    Raised when a matching Ethernet interface cannot be found
    """
    pass

class RedfishManagerResetNotFoundError( Exception ):
    """
    Raised when the Reset action cannot be found
    """
    pass

def get_manager_ids( context ):
    """
    Finds the manager collection and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list of identifiers of the members of the manager collection
    """

    # Get the service root to find the manager collection
    service_root = context.get( "/redfish/v1/" )
    if "Managers" not in service_root.dict:
        # No manager collection
        raise RedfishManagerNotFoundError( "Service does not contain a manager collection" )

    # Get the manager collection and iterate through its collection
    avail_managers = []
    manager_col = context.get( service_root.dict["Managers"]["@odata.id"] )
    while True:
        for manager_member in manager_col.dict["Members"]:
            avail_managers.append( manager_member["@odata.id"].strip( "/" ).split( "/" )[-1] )
        if "Members@odata.nextLink" not in manager_col.dict:
            break
        manager_col = context.get( manager_col.dict["Members@odata.nextLink"] )
    return avail_managers

def get_manager( context, manager_id = None ):
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
        manager = context.get( manager_uri_pattern.format( manager_id ) )
    # No identifier given; see if there's exactly one member
    else:
        avail_managers = get_manager_ids( context )
        if len( avail_managers ) == 1:
            manager = context.get( manager_uri_pattern.format( avail_managers[0] ) )
        else:
            raise RedfishManagerNotFoundError( "Service does not contain exactly one manager; a target manager needs to be specified: {}".format( ", ".join( avail_managers ) ) )

    # Check the response and return the manager if the response is good
    try:
        verify_response( manager )
    except:
        if avail_managers is None:
            avail_managers = get_manager_ids( context )
        raise RedfishManagerNotFoundError( "Service does not contain a manager called {}; valid managers: {}".format( manager_id, ", ".join( avail_managers ) ) ) from None
    return manager

def print_manager( manager ):
    """
    Prints the manager info

    Args:
        manager: The manager info to print
    """

    manager_line_format = "  {}: {}"
    manager_properties = [ "Status", "ManagerType", "PowerState", "FirmwareVersion", "DateTime", "DateTimeLocalOffset", "LastResetTime",
        "UUID", "ServiceEntryPointUUID", "Manufacturer", "Model", "PartNumber", "SparePartNumber", "SerialNumber" ]
    print( "Manager {} Info".format( manager.dict["Id"] ) )
    for property in manager_properties:
        if property in manager.dict:
            prop_val = manager.dict[property]
            if isinstance( prop_val, list ):
                prop_val = ", ".join( prop_val )
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format( prop_val.get( "State", "N/A" ), prop_val.get( "Health", "N/A" ) )
            print( manager_line_format.format( property, prop_val ) )
    print( "" )

def get_manager_reset_info( context, manager_id = None, manager = None ):
    """
    Finds a manager matching the given ID and returns its reset info

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        manager: Existing manager resource to inspect for reset info

    Returns:
        The URI of the Reset action
        A list of parameter requirements from the Action Info
    """

    if manager is None:
        manager = get_manager( context, manager_id )

    # Check that there is a Reset action
    if "Actions" not in manager.dict:
        raise RedfishManagerResetNotFoundError( "Manager does not support Reset" )
    if "#Manager.Reset" not in manager.dict["Actions"]:
        raise RedfishManagerResetNotFoundError( "Manager does not support Reset" )

    # Extract the info about the SimpleUpdate action
    reset_action = manager.dict["Actions"]["#Manager.Reset"]
    reset_uri = reset_action["target"]

    if "@Redfish.ActionInfo" not in reset_action:
        # No Action Info; need to build this manually based on other annotations

        # Default parameter requirements
        reset_parameters = [
            {
                "Name": "ResetType",
                "Required": False,
                "DataType": "String",
                "AllowableValues": reset_types
            }
        ]

        # Get the AllowableValues from annotations
        for param in reset_parameters:
            if param["Name"] + "@Redfish.AllowableValues" in reset_action:
                param["AllowableValues"] = reset_action[param["Name"] + "@Redfish.AllowableValues"]
    else:
        # Get the Action Info and its parameter listing
        action_info = context.get( reset_action["@Redfish.ActionInfo"] )
        reset_parameters = action_info.dict["Parameters"]

    return reset_uri, reset_parameters

def manager_reset( context, manager_id = None, reset_type = None ):
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
            raise ValueError( "{} is not an allowable reset type ({})".format( reset_type, ", ".join( reset_type_values ) ) )

    # Locate the reset action
    reset_uri, reset_parameters = get_manager_reset_info( context, manager_id )

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
    response = context.post( reset_uri, body = payload )
    verify_response( response )
    return response

def get_manager_ethernet_interface_ids( context, manager_id = None ):
    """
    Finds the Ethernet interface collection for a manager and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager

    Returns:
        A list of identifiers of the members of the Ethernet interface collection
    """

    # Get the manager to find its Ethernet interface collection
    manager = get_manager( context, manager_id )
    if "EthernetInterfaces" not in manager.dict:
        # No Ethernet interface collection
        raise RedfishManagerEthIntNotFoundError( "Manager {} does not contain an Ethernet interface collection".format( manager.dict["Id"] ) )

    # Get the Ethernet interface collection and iterate through its collection
    avail_interfaces = []
    interface_col = context.get( manager.dict["EthernetInterfaces"]["@odata.id"] )
    while True:
        for interface_member in interface_col.dict["Members"]:
            avail_interfaces.append( interface_member["@odata.id"].strip( "/" ).split( "/" )[-1] )
        if "Members@odata.nextLink" not in interface_col.dict:
            break
        interface_col = context.get( interface_col.dict["Members@odata.nextLink"] )
    return avail_interfaces

def get_manager_ethernet_interface( context, manager_id = None, interface_id = None ):
    """
    Finds an Ethernet interface for a manager matching the given identifiers and returns its resource

    Args:
        context: The Redfish client object with an open session
        manager_id: The manager to locate; if None, perform on the only manager
        interface_id: The Ethernet interface to locate; if None, perform on the only Ethernet interface

    Returns:
        The manager resource
    """

    interface_uri_pattern = "/redfish/v1/Managers/{}/EthernetInterfaces/{}"
    avail_interfaces = None

    # Get the manager identifier in order to build the full URI later
    if manager_id is None:
        manager = get_manager( context, None )
        manager_id = manager.dict["Id"]

    # If given an identifier, get the Ethernet interface directly
    if interface_id is not None:
        interface = context.get( interface_uri_pattern.format( manager_id, interface_id ) )
    # No identifier given; see if there's exactly one member
    else:
        avail_interfaces = get_manager_ethernet_interface_ids( context, manager_id )
        if len( avail_interfaces ) == 1:
            interface = context.get( interface_uri_pattern.format( manager_id, avail_interfaces[0] ) )
        else:
            raise RedfishManagerEthIntNotFoundError( "Manager {} does not contain exactly one Ethernet interface; a target Ethernet interface needs to be specified: {}".format( manager_id, ", ".join( avail_interfaces ) ) )

    # Check the response and return the Ethernet interface if the response is good
    try:
        verify_response( interface )
    except:
        if avail_interfaces is None:
            avail_interfaces = get_manager_ethernet_interface_ids( context, manager_id )
        raise RedfishManagerEthIntNotFoundError( "Manager {} does not contain an Ethernet interface called {}; valid Ethernet interfaces: {}".format( manager_id, interface_id, ", ".join( avail_interfaces ) ) ) from None
    return interface

def set_manager_ethernet_interface( context, manager_id = None, interface_id = None, vlan = None, ipv4_addresses = None, dhcpv4 = None, ipv6_addresses = None, ipv6_gateways = None, dhcpv6 = None ):
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
    interface = get_manager_ethernet_interface( context, manager_id, interface_id )

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
    etag = interface.getheader( "ETag" )
    if etag is not None:
        headers = { "If-Match": etag }
    response = context.patch( interface.dict["@odata.id"], body = payload, headers = headers )
    verify_response( response )
    return response

def print_manager_ethernet_interface( interface ):
    """
    Prints the Ethernet interface info

    Args:
        interface: The Ethernet interface info to print
    """

    interface_line_format = "  {}: {}"
    interface_properties = [ "Status", "InterfaceEnabled", "LinkStatus", "MACAddress", "PermanentMACAddress", "SpeedMbps", "AutoNeg", "FullDuplex",
        "MTUSize", "HostName", "FQDN", "NameServers", "StaticNameServers" ]
    print( "Ethernet Interface {} Info".format( interface.dict["Id"] ) )
    for property in interface_properties:
        if property in interface.dict:
            prop_val = interface.dict[property]
            if isinstance( prop_val, list ):
                prop_val = ", ".join( prop_val )
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format( prop_val.get( "State", "N/A" ), prop_val.get( "Health", "N/A" ) )
            print( interface_line_format.format( property, prop_val ) )
    print( "" )

    if "VLAN" in interface.dict:
        print( "  VLAN Info" )
        print( "    Enabled: {}".format( interface.dict["VLAN"].get( "VLANEnable", False ) ) )
        print( "    ID: {}".format( interface.dict["VLAN"].get( "VLANId", "N/A" ) ) )
        print( "    Priority: {}".format( interface.dict["VLAN"].get( "VLANPriority", "N/A" ) ) )
        print( "" )

    print( "  IPv4 Info" )
    if "DHCPv4" in interface.dict:
        print( "    DHCP Enabled: {}".format( interface.dict["DHCPv4"]["DHCPEnabled"] ) )
    if "IPv4Addresses" in interface.dict:
        print( "    Assigned Addresses" )
        for i, address in enumerate( interface.dict["IPv4Addresses"] ):
            if address is None:
                print( "      Empty" )
            elif i == 0:
                print( "      {}: {}, {}, {}".format( address.get( "Address", "N/A" ), address.get( "SubnetMask", "N/A" ), address.get( "Gateway", "N/A" ), address.get( "AddressOrigin", "N/A" ) ) )
            else:
                print( "      {}: {}, {}".format( address.get( "Address", "N/A" ), address.get( "SubnetMask", "N/A" ), address.get( "AddressOrigin", "N/A" ) ) )
    if "IPv4StaticAddresses" in interface.dict:
        print( "    Static Addresses" )
        for i, address in enumerate( interface.dict["IPv4StaticAddresses"] ):
            if address is None:
                print( "       Empty" )
            elif i == 0:
                print( "      {}: {}, {}".format( address.get( "Address", "N/A" ), address.get( "SubnetMask", "N/A" ), address.get( "Gateway", "N/A" ) ) )
            else:
                print( "      {}: {}".format( address["Address"], address["SubnetMask"] ) )
    print( "" )

    print( "  IPv6 Info" )
    if "DHCPv6" in interface.dict:
        print( "    DHCP Mode: {}".format( interface.dict["DHCPv6"]["OperatingMode"] ) )
    if "IPv6Addresses" in interface.dict:
        print( "    Assigned Addresses" )
        for address in interface.dict["IPv6Addresses"]:
            print( "      {}/{}: {}, {}".format( address.get( "Address", "N/A" ), address.get( "PrefixLength", "N/A" ), address.get( "AddressOrigin", "N/A" ), address.get( "AddressState", "N/A" ) ) )
    if "IPv6StaticAddresses" in interface.dict:
        print( "    Static Addresses" )
        for address in interface.dict["IPv6StaticAddresses"]:
            if address is None:
                print( "      Empty" )
            else:
                print( "      {}/{}".format( address.get( "Address", "N/A" ), address.get( "PrefixLength", "N/A" ) ) )
    if "IPv6StaticDefaultGateways" in interface.dict:
        print( "    Static Default Gateways" )
        for address in interface.dict["IPv6StaticDefaultGateways"]:
            if address is None:
                print( "      Empty" )
            else:
                print( "      {}/{}".format( address.get( "Address", "N/A" ), address.get( "PrefixLength", "N/A" ) ) )
    if "IPv6DefaultGateway" in interface.dict:
        print( "    Default Gateway: {}".format( interface.dict["IPv6DefaultGateway"] ) )
    if "IPv6AddressPolicyTable" in interface.dict:
        print( "    Address Policy Table" )
        for policy in interface.dict["IPv6AddressPolicyTable"]:
            if policy is None:
                print( "      Empty" )
            else:
                print( "      Prefix: {}, Prec: {}, Label: {}".format( policy.get( "Prefix", "N/A" ), policy.get( "Precedence", "N/A" ), policy.get( "Label", "N/A" ) ) )
    print( "" )