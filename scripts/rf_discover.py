#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Discover

File : rf_discover.py

Brief : This script uses the redfish module to discover Redfish services
"""

import argparse
import re
import redfish

# No arguments, but having help text is useful
argget = argparse.ArgumentParser( description = "A tool to discover Redfish services" )
args = argget.parse_args()

# Invoke the discovery routine for SSDP and print the responses
services = redfish.discover_ssdp()
if len( services ) == 0:
    print( "No Redfish services discovered" )
else:
    print( "Redfish services:" )

# Go through each discovered service and print out basic info
for service in services:
    # Try to get the Product property from the service root for each service
    # If found, print the UUID, service root pointer, and the Product
    # If not, just print the UUID and service root pointer
    try:
        # Need to strip off /redfish/v1 from the SSDP response to use the URL with the library
        groups = re.search( "^(.+)\/redfish\/v1\/?$", services[service] )
        url = groups.group( 1 )
        redfish_obj = redfish.redfish_client( base_url = url )
        print( "{}: {} ({})".format( service, services[service], redfish_obj.root["Product"] ) )
    except:
        print( "{}: {}".format( service, services[service] ) )
