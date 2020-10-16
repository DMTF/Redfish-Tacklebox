#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Messages Module

File : messages.py

Brief : This file contains the definitions and functionalities for interacting
        with Messages for a given Redfish service
"""

class RedfishOperationFailedError( Exception ):
    """
    Raised when an operation has failed (HTTP Status >= 400)
    """
    pass

def print_error_payload( response ):
    """
    Prints an error payload, which can also be used for action responses

    Args:
        response: The response to print
    """

    # Check if this response has no body
    if response.dict is None:
        if response.status >= 400:
            print( "Failed" )
        else:
            print( "Success" )
        return

    print( get_error_messages( response ) )

def get_error_messages( response ):
    """
    Builds a string based on the error messages in the payload

    Args:
        response: The response to print

    Returns:
        The string containing error messages
    """

    # Pull out the error payload and the messages
    out_string = response.dict["error"]["message"]
    if "@Message.ExtendedInfo" in response.dict["error"]:
        for message in response.dict["error"]["@Message.ExtendedInfo"]:
            if "Message" in message:
                out_string = out_string + "\n" + message["Message"]
            else:
                out_string = out_string + "\n" + message["MessageId"]

    return out_string

def verify_response( response ):
    """
    Verifies a response and raises an exception if there was a failure

    Args:
        response: The response to verify
    """

    if response.status >= 400:
        exception_string = get_error_messages( response )
        raise RedfishOperationFailedError( "Operation failed: HTTP {}\n{}".format( response.status, exception_string ) )

    return
