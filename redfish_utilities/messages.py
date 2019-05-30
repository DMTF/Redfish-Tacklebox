#! /usr/bin/python
# Copyright Notice:
# Copyright 2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Messages Module

File : messages.py

Brief : This file contains the definitions and functionalities for interacting
        with Messages for a given Redfish service
"""

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

    # Pull out the error payload and the messages
    print( response.dict["error"]["message"] )
    if "@Message.ExtendedInfo" in response.dict["error"]:
        for message in response.dict["error"]["@Message.ExtendedInfo"]:
            if "Message" in message:
                print( message["Message"] )
            else:
                print( message["MessageId"] )
