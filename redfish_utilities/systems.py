#! /usr/bin/python
# Copyright Notice:
# Copyright 2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Systems Module

File : systems.py

Brief : This file contains the definitions and functionalities for interacting
        with the Systems Collection for a given Redfish service
"""

from .messages import verify_response

class RedfishSystemNotFoundError( Exception ):
    """
    Raised when a matching system cannot be found
    """
    pass

class RedfishSystemResetNotFoundError( Exception ):
    """
    Raised when the Reset action cannot be found
    """
    pass

def get_system_boot( context, system_id = None ):
    """
    Finds a system matching the given ID and returns its Boot object

    Args:
        context: The Redfish client object with an open session
        system_id: The system to locate; if None, perform on the only system

    Returns:
        The Boot object from the given system
    """

    system = get_system( context, system_id )
    return system.dict["Boot"]

def set_system_boot( context, system_id = None, ov_target = None, ov_enabled = None, ov_mode = None, ov_uefi_target = None, ov_boot_next = None ):
    """
    Finds a system matching the given ID and updates its Boot object

    Args:
        context: The Redfish client object with an open session
        system_id: The system to locate; if None, perform on the only system
        ov_target: The override target (BootSourceOverrideTarget)
        ov_enabled: The override enabled setting (BootSourceOverrideEnabled)
        ov_mode: The override mode setting (BootSourceOverrideMode)
        ov_uefi_target: The UEFI target for override (UefiTargetBootSourceOverride)
        ov_boot_next: The UEFI boot next for override (BootNext)

    Returns:
        The response of the PATCH
    """

    # Check that the values themselves are supported by the schema
    ov_target_values = [ "None", "Pxe", "Floppy", "Cd", "Usb", "Hdd", "BiosSetup", "Utilities", "Diags",
                         "UefiShell", "UefiTarget", "SDCard", "UefiHttp", "RemoteDrive", "UefiBootNext" ]
    if ov_target is not None:
        if ov_target not in ov_target_values:
            raise ValueError( "{} is not an allowable override target ({})".format( ov_target, ", ".join( ov_target_values ) ) )
    ov_enabled_values = [ "Disabled", "Once", "Continuous" ]
    if ov_enabled is not None:
        if ov_enabled not in ov_enabled_values:
            raise ValueError( "{} is not an allowable override enabled ({})".format( ov_enabled, ", ".join( ov_enabled_values ) ) )
    ov_mode_values = [ "Legacy", "UEFI" ]
    if ov_mode is not None:
        if ov_mode not in ov_mode_values:
            raise ValueError( "{} is not an allowable override mode ({})".format( ov_mode, ", ".join( ov_mode_values ) ) )

    # Locate the system
    system = get_system( context, system_id )

    # Build the payload
    payload = { "Boot": {} }
    if ov_target is not None:
        payload["Boot"]["BootSourceOverrideTarget"] = ov_target
    if ov_enabled is not None:
        payload["Boot"]["BootSourceOverrideEnabled"] = ov_enabled
    if ov_mode is not None:
        payload["Boot"]["BootSourceOverrideMode"] = ov_mode
    if ov_uefi_target is not None:
        payload["Boot"]["UefiTargetBootSourceOverride"] = ov_uefi_target
    if ov_boot_next is not None:
        payload["Boot"]["BootNext"] = ov_boot_next

    # Update the system
    response = context.patch( system.dict["@odata.id"], body = payload )
    verify_response( response )
    return response

def print_system_boot( boot ):
    """
    Prints the contents of a Boot object

    Args:
        boot: The Boot object to print
    """

    print( "" )

    print( "Boot Override Settings:" )
    boot_properties = [ "BootSourceOverrideTarget", "BootSourceOverrideEnabled", "BootSourceOverrideMode", "UefiTargetBootSourceOverride", "BootNext" ]
    boot_strings = [ "Target", "Enabled", "Mode", "UEFI Target", "Boot Next" ]
    for index, boot_property in enumerate( boot_properties ):
        if boot_property in boot:
            out_string = "  {}: {}".format( boot_strings[index], boot[boot_property] )
            allow_string = ""
            if boot_property + "@Redfish.AllowableValues" in boot:
                allow_string = "; Allowable Values: {}".format( ", ".join( boot[boot_property + "@Redfish.AllowableValues"] ) )
            print( out_string + allow_string )

    print( "" )

def get_system_reset_info( context, system_id = None ):
    """
    Finds a system matching the given ID and returns its reset info

    Args:
        context: The Redfish client object with an open session
        system_id: The system to locate; if None, perform on the only system

    Returns:
        The URI of the Reset action
        A list of parameter requirements from the Action Info
    """

    system = get_system( context, system_id )

    # Check that there is a Reset action
    if "Actions" not in system.dict:
        raise RedfishSystemResetNotFoundError( "System does not support Reset" )
    if "#ComputerSystem.Reset" not in system.dict["Actions"]:
        raise RedfishSystemResetNotFoundError( "System does not support Reset" )

    # Extract the info about the SimpleUpdate action
    reset_action = system.dict["Actions"]["#ComputerSystem.Reset"]
    reset_uri = reset_action["target"]

    if "@Redfish.ActionInfo" not in reset_action:
        # No Action Info; need to build this manually based on other annotations

        # Default parameter requirements
        reset_parameters = [
            {
                "Name": "ResetType",
                "Required": False,
                "DataType": "String",
                "AllowableValues": [ "On", "ForceOff", "GracefulShutdown", "GracefulRestart", "ForceRestart", "Nmi", "ForceOn", "PushPowerButton", "PowerCycle" ]
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

def system_reset( context, system_id = None, reset_type = None ):
    """
    Finds a system matching the given ID and performs a reset

    Args:
        context: The Redfish client object with an open session
        system_id: The system to locate; if None, perform on the only system
        reset_type: The type of reset to perform; if None, perform one of the common resets

    Returns:
        The response of the action
    """

    # Check that the values themselves are supported by the schema
    reset_type_values = [ "On", "ForceOff", "GracefulShutdown", "GracefulRestart", "ForceRestart", "Nmi", "ForceOn", "PushPowerButton", "PowerCycle" ]
    if reset_type is not None:
        if reset_type not in reset_type_values:
            raise ValueError( "{} is not an allowable reset type ({})".format( reset_type, ", ".join( reset_type_values ) ) )

    # Locate the reset action
    reset_uri, reset_parameters = get_system_reset_info( context, system_id )

    # Build the payload
    if reset_type is None:
        for param in reset_parameters:
            if param["Name"] == "ResetType":
                if "GracefulRestart" in param["AllowableValues"]:
                    reset_type = "GracefulRestart"
                elif "PushPowerButton" in param["AllowableValues"]:
                    reset_type = "PushPowerButton"
                elif "ForceRestart" in param["AllowableValues"]:
                    reset_type = "ForceRestart"
                elif "PowerCycle" in param["AllowableValues"]:
                    reset_type = "PowerCycle"

    payload = {}
    if reset_type is not None:
        payload["ResetType"] = reset_type

    # Reset the system
    response = context.post( reset_uri, body = payload )
    verify_response( response )
    return response

def get_system( context, system_id = None ):
    """
    Finds a system matching the given ID and returns its resource

    Args:
        context: The Redfish client object with an open session
        system_id: The system to locate; if None, perform on the only system

    Returns:
        The system resource
    """

    # Get the Service Root to find the System Collection
    service_root = context.get( "/redfish/v1/" )
    if "Systems" not in service_root.dict:
        # No System collection
        raise RedfishSystemNotFoundError( "Service does not contain a Systems Collection" )

    # Get the System Collection and iterate through its collection
    system_col = context.get( service_root.dict["Systems"]["@odata.id"] )
    if system_id is None:
        if len( system_col.dict["Members"] ) == 1:
            return context.get( system_col.dict["Members"][0]["@odata.id"] )
        else:
            raise RedfishSystemNotFoundError( "Service does not contain exactly one system; a target system needs to be specified" )
    else:
        for system_member in system_col.dict["Members"]:
            system = context.get( system_member["@odata.id"] )
            if system.dict["Id"] == system_id:
                return system

    raise RedfishSystemNotFoundError( "Service does not contain a system called {}".format( system_id ) )
