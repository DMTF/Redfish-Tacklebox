#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Raw Request

File : rf_raw_request.py

Brief : This script performs a raw request specified by the user
"""

import argparse
import json
import redfish

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool perform a raw request to a Redfish service" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--verbose", "-v", action = "store_true", help = "Indicates if HTTP response codes and headers are displayed", default = False )
argget.add_argument( "--request", "-req", type = str, required = True, nargs = "+", help = "The method, URI, and body for the request; if the method is not provided, GET is performed" )
args = argget.parse_args()

# Extract and verify the request
allowed_methods = [ "GET", "HEAD", "POST", "PATCH", "PUT", "DELETE" ]
method = "GET"
uri = None
body = None
if len( args.request ) == 1:
    uri = args.request[0]
else:
    method = args.request[0]
    uri = args.request[1]
    if len( args.request ) > 2:
        body = args.request[2]
if method.upper() not in allowed_methods:
    print( "Invalid method: {} (choose from {})".format( method, ", ".join( allowed_methods ) ) )
    exit( 2 )
method = method.upper()

# Connect to the service
with redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password ) as redfish_obj:
    # Encode the body as a dictionary
    try:
        body = json.loads( body )
    except:
        # Not valid JSON; try passing it into the request as a string
        pass

    # Perform the requested operation
    if method == "HEAD":
        resp = redfish_obj.head( uri )
    elif method == "POST":
        resp = redfish_obj.post( uri, body = body )
    elif method == "PATCH":
        resp = redfish_obj.patch( uri, body = body )
    elif method == "PUT":
        resp = redfish_obj.put( uri, body = body )
    elif method == "DELETE":
        resp = redfish_obj.head( uri )
    else:
        resp = redfish_obj.get( uri )

    # Print HTTP status and headers
    if args.verbose:
        print( "HTTP {}".format( resp.status ) )
        for header in resp.getheaders():
            print( "{}: {}".format( header[0], header[1] ) )
        print()

    # Print the response
    try:
        print( json.dumps( resp.dict, sort_keys = True, indent = 4, separators = ( ",", ": " ) ) )
    except:
        # The response is either malformed JSON or not JSON at all
        print( resp.text )
