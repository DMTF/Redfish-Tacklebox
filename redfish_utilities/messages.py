#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Messages Module

File : messages.py

Brief : This file contains the definitions and functionalities for interacting
        with Messages for a given Redfish service
"""

from redfish.messages import *

def verify_response( response ):
    """
    Verifies a response and raises an exception if there was a failure

    Args:
        response: The response to verify
    """

    if response.status >= 400:
        messages_detail = get_messages_detail( response )
        exception_string = get_error_messages( messages_detail )
        message_item = search_message( messages_detail, "Base", "PasswordChangeRequired" )
        if not message_item is None:
            raise RedfishPasswordChangeRequiredError( "Operation failed: HTTP {}\n{}".format( response.status, exception_string ), message_item["MessageArgs"][0] )
        else:
            raise RedfishOperationFailedError( "Operation failed: HTTP {}\n{}".format( response.status, exception_string ) )

    return

def print_error_payload( response ):
    """
    Prints an error payload, which can also be used for action responses

    Args:
        response: The response to print
    """

    try:
        print( get_error_messages( response ) )
    except:
        # No response body
        if response.status >= 400:
            print( "Failed" )
        else:
            print( "Success" )
