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
argget.add_argument( "--method", "-m", type = str, required = False, help = "The HTTP method to perform; performs GET if not specified", default = "GET", choices = [ "GET", "HEAD", "POST", "PATCH", "PUT", "DELETE" ] )
argget.add_argument( "--request", "-req", type = str, required = True, help = "The URI for the request" )
argget.add_argument( "--body", "-b", type = str, required = False, help = "The body to provide with the request" )
argget.add_argument( "--verbose", "-v", action = "store_true", help = "Indicates if HTTP response codes and headers are displayed", default = False )
args = argget.parse_args()

# Connect to the service
with redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password ) as redfish_obj:
    # Encode the body as a dictionary
    try:
        body = json.loads( args.body )
    except:
        # Not valid JSON; try passing it into the request as a string
        body = args.body

    # Perform the requested operation
    if args.method == "HEAD":
        resp = redfish_obj.head( args.request )
    elif args.method == "POST":
        resp = redfish_obj.post( args.request, body = body )
    elif args.method == "PATCH":
        resp = redfish_obj.patch( args.request, body = body )
    elif args.method == "PUT":
        resp = redfish_obj.put( args.request, body = body )
    elif args.method == "DELETE":
        resp = redfish_obj.delete( args.request )
    else:
        resp = redfish_obj.get( args.request )

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
