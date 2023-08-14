#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Update Module

File : update.py

Brief : This file contains the definitions and functionalities for interacting
        with the UpdateService for a given Redfish service
"""

import json
import os
import errno
import math
from .messages import verify_response

class RedfishUpdateServiceNotFoundError( Exception ):
    """
    Raised when the update service or an update action cannot be found
    """
    pass

def get_simple_update_info( context ):
    """
    Locates the SimpleUpdate action and collects its information

    Args:
        context: The Redfish client object with an open session

    Returns:
        The URI of the SimpleUpdate action
        A list of parameter requirements from the action info
    """

    # Get the update service
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
        # No action info; need to build this manually based on other annotations

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

        # Get the allowable values from annotations
        for param in simple_update_parameters:
            if param["Name"] + "@Redfish.AllowableValues" in simple_update_action:
                param["AllowableValues"] = simple_update_action[param["Name"] + "@Redfish.AllowableValues"]
    else:
        # Get the action info and its parameter listing
        action_info = context.get( simple_update_action["@Redfish.ActionInfo"] )
        simple_update_parameters = action_info.dict["Parameters"]

    return simple_update_uri, simple_update_parameters

def simple_update( context, image_uri, protocol = None, targets = None, username = None, password = None ):
    """
    Performs a SimpleUpdate request

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

    # Get the SimpleUpdate info
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

def get_size( file_path, unit = 'bytes' ):
    """
    Determines the size of a local file

    Args:
        file_path: The path to the file
        unit: The units to apply to the return value

    Returns:
        The size of the file in the specified units
    """

    file_size = os.path.getsize( file_path )
    exponents_map = { 'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3 }
    if unit not in exponents_map:
        raise ValueError( "Must select from ['bytes', 'kb', 'mb', 'gb']" )
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return round( size, 3 )
    
def multipart_push_update( context, image_path, targets = None, timeout = None ):
    """
    Performs an HTTP Multipart push update request

    Args:
        context: The Redfish client object with an open session
        image_path: The filepath to the image for the update
        targets: The targets receiving the update
        timeout: The timeout to apply to the update

    Returns:
        The response from the request
    """

    # Ensure the file exists
    if os.path.isfile( image_path ) is False:
        raise FileNotFoundError( errno.ENOENT, os.strerror( errno.ENOENT ), image_path )

    # If no update is specified, determine an appropriate timeout to apply
    if timeout is None:
        """TODO: See what a 'reasonable' timeout is when accounting for slow networks
        for now, keeping the timeout conservative (2 seconds per MB)
        timeout = 5
        file_size = get_size( image_path, "mb" )

        if file_size >= 16:
            timeout = math.ceil( ( 5 / 16 ) * file_size )
        """
        timeout = 30
        file_size = get_size( image_path, "mb" )
        if file_size >= 15:
            timeout = 2 * file_size

    # Get the update service
    update_service = get_update_service( context )
    if "MultipartHttpPushUri" not in update_service.dict:
        raise RedfishUpdateServiceNotFoundError( "Service does not support MultipartHttpPushUri" )

    # Build the request body
    update_parameters = {}
    if targets is not None:
        update_parameters["Targets"] = targets
    body = {
        "UpdateParameters": ( None, json.dumps( update_parameters ), "application/json" ),
        "UpdateFile": ( image_path.split( os.path.sep )[-1], open( image_path, "rb" ), "application/octet-stream" )
    }

    response = context.post( update_service.dict["MultipartHttpPushUri"], body = body, headers = { "Content-Type": "multipart/form-data" }, timeout = timeout, max_retry = 3 )
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
