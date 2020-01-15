#! /usr/bin/python
# Copyright Notice:
# Copyright 2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish Discover

File : rf_discover.py

Brief : This script uses the redfish module to discover Redfish services
"""

import argparse
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
for service in services:
    print( "{}: {}".format( service, services[service] ) )
