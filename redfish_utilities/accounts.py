#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Accounts Module

File : accounts.py

Brief : This file contains the definitions and functionalities for managing
        accounts on a Redfish Service
"""

from .messages import verify_response

class RedfishAccountCollectionNotFoundError( Exception ):
    """
    Raised when the Account Service or Account Collection cannot be found
    """
    pass

class RedfishAccountNotFoundError( Exception ):
    """
    Raised when the Account Service or Account Collection cannot be found
    """
    pass

class RedfishAccountNotAddedError( Exception ):
    """
    Raised when the requested account was not added
    """
    pass

def get_users( context ):
    """
    Collects user information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all users
    """

    user_list = []

    # Go through each Account in the Account Collection
    account_col = context.get( get_account_collection( context ), None )
    for account_member in account_col.dict["Members"]:
        account = context.get( account_member["@odata.id"], None )
        account_info = {
            "UserName": account.dict["UserName"],
            "RoleId": account.dict["RoleId"],
            "Locked": account.dict.get( "Locked", False ),
            "Enabled": account.dict.get( "Enabled", True )
        }

        # Some implementations always expose "slots" for users; ignore empty slots
        if account_info["UserName"] == "" and account_info["Enabled"] == False:
            continue

        user_list.append( account_info )

    return user_list

def print_users( user_list ):
    """
    Prints the user list into a table

    Args:
        user_list: The user list to print
    """

    user_line_format = "  {:20s} | {:20s} | {:10s} | {:10s}"
    print( "" )
    print( user_line_format.format( "Name", "Role", "Locked", "Enabled" ) )
    for user in user_list:
        print( user_line_format.format( user["UserName"], user["RoleId"], str( user["Locked"] ), str( user["Enabled"] ) ) )
    print( "" )

def add_user( context, user_name, password, role ):
    """
    Adds a new user account

    Args:
        context: The Redfish client object with an open session
        user_name: The name of the user to add
        password: The password for the new user
        role: The role for the new user

    Returns:
        The response of the POST
    """

    # Create the new user
    payload = {
        "UserName": user_name,
        "Password": password,
        "RoleId": role
    }
    account_col_uri = get_account_collection( context )
    response = context.post( account_col_uri, body = payload )
    if response.status == 405:
        # Some implementations allocate slots for users and don't allow adding in the proper sense
        # Find an empty slot to use
        account_added = False
        account_col = context.get( account_col_uri )
        for account_member in account_col.dict["Members"]:
            account = context.get( account_member["@odata.id"] )
            if account.dict["UserName"] == "" and not account.dict.get( "Enabled", True ):
                # Empty slot found; PATCH it
                response = context.patch( account_member["@odata.id"], body = payload, headers = { "If-Match": account.getheader( "ETag" ) } )
                if response.status < 400:
                    # These implementations also might restrict which slots to modify...
                    account_added = True
                    break
        if not account_added:
            raise RedfishAccountNotAddedError( "Failed to add user '{}'; user may already exist or there is not enough space for the new user".format( user_name ) )
    verify_response( response )
    return response

def delete_user( context, user_name ):
    """
    Deletes an existing user account

    Args:
        context: The Redfish client object with an open session
        user_name: The name of the user to delete

    Returns:
        The response of the DELETE
    """

    # Find the user to delete
    user_uri, user_info = get_user( context, user_name )

    # Delete the user
    response = context.delete( user_uri )
    if response.status == 405:
        # Some implementations keep slots around and don't allow for deleting in the proper sense
        # Some also do not allow for both Enabled and UserName to be modified simultaneously
        modify_user( context, user_name, new_enabled = False )
        return modify_user( context, user_name, new_name = "" )
    verify_response( response )
    return response

def modify_user( context, user_name, new_name = None, new_password = None, new_role = None, new_locked = None, new_enabled = None ):
    """
    Modifies an existing user account

    Args:
        context: The Redfish client object with an open session
        user_name: The name of the user to modify
        new_name: The new name of the user
        new_password: The new password of the user
        new_role: The new role of the user
        new_locked: The new locked flag of the user
        new_enabled: The new enabled flag of the user

    Returns:
        The response of the PATCH
    """

    # Get the current user info
    user_uri, user_info = get_user( context, user_name )

    # Build the payload for the new user
    new_info = {}
    if new_name is not None:
        new_info["UserName"] = new_name
    if new_password is not None:
        new_info["Password"] = new_password
    if new_role is not None:
        new_info["RoleId"] = new_role
    if new_locked is not None:
        new_info["Locked"] = new_locked
    if new_enabled is not None:
        new_info["Enabled"] = new_enabled

    # Update the user
    response = context.patch( user_uri, body = new_info, headers = { "If-Match": user_info.getheader( "ETag" ) } )
    verify_response( response )
    return response

def get_account_collection( context ):
    """
    Finds the account collection for the Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        The URI for the account collection
    """

    # Get the Service Root to find the Account Service
    service_root = context.get( "/redfish/v1/" )
    if "AccountService" not in service_root.dict:
        # No Account Service
        raise RedfishAccountCollectionNotFoundError( "Service does not contain an Account Service" )

    # Get the Account Service to find the Account Collection
    account_service = context.get( service_root.dict["AccountService"]["@odata.id"] )
    if "Accounts" not in account_service.dict:
        # No Account Collection
        raise RedfishAccountCollectionNotFoundError( "Service does not contain an Account Collection" )

    return account_service.dict["Accounts"]["@odata.id"]

def get_user( context, user_name ):
    """
    Finds a user within the Redfish service

    Args:
        context: The Redfish client object with an open session
        user_name: The name of the user to find

    Returns:
        The URI for the user account
        The contents of the user account resource
    """

    avail_users = []
    account_col = context.get( get_account_collection( context ) )
    for account_member in account_col.dict["Members"]:
        account = context.get( account_member["@odata.id"] )

        # Some implementations always expose "slots" for users; ignore empty slots
        if account.dict["UserName"] == "" and not account.dict.get( "Enabled", True ):
            continue

        avail_users.append( account.dict["UserName"] )

        # Check if the name matches
        if account.dict["UserName"] == user_name:
            return account_member["@odata.id"], account

    # No matches found
    raise RedfishAccountCollectionNotFoundError( "User '{}' is not found; valid users: {}".format( user_name, ", ".join( avail_users ) ) )
