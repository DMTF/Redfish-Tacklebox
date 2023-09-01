#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2023 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Certificates

File : rf_certificates.py

Brief : This script uses the redfish_utilities module to manage certificates
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback
import sys
from redfish.messages import RedfishPasswordChangeRequiredError

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to manage certificates on a Redfish service" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
subparsers = argget.add_subparsers( dest = "command" )
info_argget = subparsers.add_parser( "info", help = "Displays information about the certificates installed on the service" )
info_argget.add_argument( "--details", "-details", action = "store_true", help = "Indicates if the full details of each certificate should be shown" )
csrinfo_argget = subparsers.add_parser( "csrinfo", help = "Displays information about options supported for generating certificate signing requests" )
csr_argget = subparsers.add_parser( "csr", help = "Generates a certificate signing request" )
csr_argget.add_argument( "--certificatecollection", "-col", type = str, required = True, help = "The URI of the certificate collection where the signed certificate will be installed" )
csr_argget.add_argument( "--commonname", "-cn", type = str, required = True, help = "The common name of the component to secure" )
csr_argget.add_argument( "--organization", "-o", type = str, required = True, help = "The name of the unit in the organization making the request" )
csr_argget.add_argument( "--organizationalunit", "-ou", type = str, required = True, help = "The name of the unit in the organization making the request" )
csr_argget.add_argument( "--city", "-l", type = str, required = True, help = "The city or locality of the organization making the request" )
csr_argget.add_argument( "--state", "-st", type = str, required = True, help = "The state, province, or region of the organization making the request" )
csr_argget.add_argument( "--country", "-c", type = str, required = True, help = "The two-letter country code of the organization making the request" )
csr_argget.add_argument( "--email", "-email", type = str, help = "The email address of the contact within the organization making the request" )
csr_argget.add_argument( "--keyalg", "-alg", type = str, help = "The type of key-pair for use with signing algorithms" )
csr_argget.add_argument( "--keylen", "-len", type = int, help = "The length of the key, in bits, if the key pair algorithm supports key size" )
csr_argget.add_argument( "--keycurve", "-curve", type = str, help = "The curve ID to use with the key if the key pair algorithm supports curves" )
csr_argget.add_argument( "--out", "-out", type = str, help = "The file, with optional path, to save the certificate signing request" )
install_argget = subparsers.add_parser( "install", help = "Installs a certificate on the service" )
install_argget.add_argument( "--destination", "-dest", type = str, required = True, help = "The installation URI of the certificate; either a certificate collection to insert, or an existing certificate to replace" )
install_argget.add_argument( "--certificate", "-cert", type = str, required = True, help = "The file, and optional path, of the certificate to install" )
install_argget.add_argument( "--key", "-key", type = str, help = "The file, and optional path, of the private key for the certificate to install" )
delete_argget = subparsers.add_parser( "delete", help = "Deletes a certificate on the service" )
delete_argget.add_argument( "--certificate", "-cert", type = str, required = True, help = "The URI of the certificate to delete" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_certificates-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_certificates Trace" )

# Set up the Redfish object
redfish_obj = None
try:
    redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password, timeout = 15, max_retry = 3 )
    redfish_obj.login( auth = "session" )
except RedfishPasswordChangeRequiredError as e:
    redfish_utilities.print_password_change_required_and_logout( redfish_obj, args )
    sys.exit( 1 )
except Exception as e:
    raise

exit_code = 0
try:
    if args.command == "csrinfo":
        csr_uri, csr_parameters = redfish_utilities.get_generate_csr_info( redfish_obj )
        if csr_parameters is None:
            print( "No generate CSR parameter information found" )
        else:
            print( "Generate CSR parameters:" )
            for param in csr_parameters:
                required = ""
                if param.get( "Required" ):
                    required = " (required)"
                allowable_values = ""
                if param.get( "AllowableValues" ):
                    allowable_values = ": " + ", ".join( param["AllowableValues"] )
                if param.get( "AllowableNumbers" ):
                    allowable_values = ": " + ", ".join( param["AllowableNumbers"] )
                if param.get( "AllowablePattern" ):
                    allowable_values = ": " + param["AllowablePattern"]
                print( "  {}{}{}".format( param["Name"], required, allowable_values ) )
    elif args.command == "csr":
        print( "Generating cerficiate signing request..." )
        response = redfish_utilities.generate_csr( redfish_obj, args.commonname, args.organization, args.organizationalunit, args.city, args.state, args.country,
            args.certificatecollection, args.email, args.keyalg, args.keylen, args.keycurve )
        response = redfish_utilities.poll_task_monitor( redfish_obj, response )
        redfish_utilities.verify_response( response )
        print( "" )
        print( response.dict["CSRString"] )
        print( "" )
        if args.out:
            with open( args.out, "w" ) as file:
                file.write( response.dict["CSRString"] )
    elif args.command == "install":
        print( "Installing {}...".format( args.certificate ) )
        response = redfish_utilities.install_certificate( redfish_obj, args.destination, args.certificate, args.key )
        response = redfish_utilities.poll_task_monitor( redfish_obj, response )
        redfish_utilities.verify_response( response )
    elif args.command == "delete":
        print( "Deleting {}...".format( args.certificate ) )
        response = redfish_utilities.delete_certificate( redfish_obj, args.certificate )
        redfish_utilities.verify_response( response )
    else:
        certificates = redfish_utilities.get_all_certificates( redfish_obj )
        if args.command == "info":
            redfish_utilities.print_certificates( certificates, details = args.details )
        else:
            redfish_utilities.print_certificates( certificates )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    redfish_utilities.logout( redfish_obj )
sys.exit( exit_code )
