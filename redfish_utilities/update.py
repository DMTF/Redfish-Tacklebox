#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Update Module

File : update.py

Brief : This file contains the definitions and functionalities for interacting
        with the UpdateService for a given Redfish service
"""

from .messages import verify_response

class RedfishUpdateServiceNotFoundError( Exception ):
    """
    Raised when the Update Service or an update action cannot be found
    """
    pass

def get_simple_update_info( context ):
    """
    Locates the SimpleUpdate action and collects its information

    Args:
        context: The Redfish client object with an open session

    Returns:
        The URI of the Simple Update action
        A list of parameter requirements from the Action Info
    """

    # Get the Update Service
    update_service = get_update_service( context )

    # Check that there is a SimpleUpdate action
    if "Actions" not in update_service.dict:
        raise RedfishUpdateServiceNotFoundError( "Service does not support SimpleUpdate" )
    if "#UpdateService.SimpleUpdate" not in update_service.dict["Actions"]:
        raise RedfishUpdateServiceNotFoundError( "Service does not support SimpleUpdate" )

    # Extract the info about the SimpleUpdate action
    simple_update_action = update_service.dict["Actions"]["#UpdateService.SimpleUpdate"]
    simple_update_uri = simple_update_action["target"]

    if "@Redfish.ActionInfo" not in simple_update_action:
        # No Action Info; need to build this manually based on other annotations

        # Default parameter requirements
        simple_update_parameters = [
            {
                "Name": "ImageURI",
                "Required": True,
                "DataType": "String"
            },
            {
                "Name": "TransferProtocol",
                "Required": False,
                "DataType": "String",
                "AllowableValues": [ "CIFS", "FTP", "SFTP", "HTTP", "HTTPS", "NSF", "SCP", "TFTP", "OEM", "NFS" ]
            },
            {
                "Name": "Targets",
                "Required": False,
                "DateType": "StringArray"
            },
            {
                "Name": "Username",
                "Required": False,
                "DataType": "String"
            },
            {
                "Name": "Password",
                "Required": False,
                "DataType": "String"
            }
        ]

        # Get the AllowableValues from annotations
        for param in simple_update_parameters:
            if param["Name"] + "@Redfish.AllowableValues" in simple_update_action:
                param["AllowableValues"] = simple_update_action[param["Name"] + "@Redfish.AllowableValues"]
    else:
        # Get the Action Info and its parameter listing
        action_info = context.get( simple_update_action["@Redfish.ActionInfo"] )
        simple_update_parameters = action_info.dict["Parameters"]

    return simple_update_uri, simple_update_parameters

def simple_update( context, image_uri, protocol = None, targets = None, username = None, password = None ):
    """
    Performs a Simple Update request

    Args:
        context: The Redfish client object with an open session
        image_uri: The image URI for the update
        protocol: The transfer protocol for the update
        targets: The targets receiving the update
        username: The username for retrieving the update for the given URI
        password: The password for retrieving the update for the given URI

    Returns:
        The response from the request
    """

    # Get the Simple Update info
    uri, params = get_simple_update_info( context )

    # Build the request body
    body = {
        "ImageURI": image_uri
    }
    if protocol is not None:
        body["TransferProtocol"] = protocol
    if targets is not None:
        body["Targets"] = targets
    if username is not None:
        body["Username"] = username
    if password is not None:
        body["Password"] = password

    response = context.post( uri, body = body )
    verify_response( response )
    return response

def get_update_service( context ):
    """
    Locates and gets the UpdateService resource

    Args:
        context: The Redfish client object with an open session

    Returns:
        The UpdateService resource
    """

    # Get the Service Root to find the Update Service
    service_root = context.get( "/redfish/v1/" )
    if "UpdateService" not in service_root.dict:
        # No Update Service
        raise RedfishUpdateServiceNotFoundError( "Service does not have an UpdateService" )

    return context.get( service_root.dict["UpdateService"]["@odata.id"] )
