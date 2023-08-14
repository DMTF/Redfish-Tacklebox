#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Update

File : rf_update.py

Brief : This script uses the redfish_utilities module to perform updates
"""

import argparse
import datetime
import logging
import os
import re
import redfish
import redfish_utilities
import shutil
import socket
import sys
import threading
import time
import traceback
from redfish.messages import RedfishPasswordChangeRequiredError

if sys.version_info > ( 3, ):
    import http.server
else:
    import SimpleHTTPServer
    import SocketServer

WEB_SERVER_PORT = 8888
WEB_SERVER_FOLDER = "rf_update_server"

def local_web_server( filepath ):
    """
    Creates a web server to host the image file

    Args:
        filepath: The filepath for the image
    """

    # Create a temporary folder and move the file to the folder
    try:
        shutil.rmtree( WEB_SERVER_FOLDER )
    except:
        pass
    os.mkdir( WEB_SERVER_FOLDER )
    shutil.copy( filepath, WEB_SERVER_FOLDER )
    os.chdir( WEB_SERVER_FOLDER )

    # Create a web server and host it out of the temporary folder
    if sys.version_info > ( 3, ):
        handler = http.server.SimpleHTTPRequestHandler
        httpd = http.server.HTTPServer( ( "", WEB_SERVER_PORT ), handler )
    else:
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer( ( "", WEB_SERVER_PORT ), handler )
    httpd.serve_forever()

    return

def print_error_payload( response ):
    """
    Prints an error payload, which can also be used for action responses

    Args:
        response: The response to print
    """

    try:
        print(redfish_utilities.get_error_messages( response ) )
    except:
        # No response body
        if response.status >= 400:
            print( "Failed" )
        else:
            print( "Success" )

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to perform an update with a Redfish service" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--image", "-i", type = str, required = True, help = "The URI or filepath of the image" )
argget.add_argument( "--target", "-t", type = str, help = "The target resource to apply the image" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_update-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_update Trace" )

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

start_path = os.getcwd()
targets = None
if args.target is not None:
    targets = [ args.target ]
exit_code = 0
try:
    # Determine what path to use to perform the update
    update_service = redfish_utilities.get_update_service( redfish_obj )
    if os.path.isfile( args.image ):
        # Local image; see if we can push the image directly
        if "MultipartHttpPushUri" in update_service.dict:
            # Perform a multipart push update
            print( "Pushing the image to the service directly; depending on the size of the image, this can take a few minutes..." )
            response = redfish_utilities.multipart_push_update( redfish_obj, args.image, targets = targets )
        else:
            # Host a local web server and perform a SimpleUpdate for the local image
            web_server_thread = threading.Thread( target = local_web_server, args=( args.image, ) )
            web_server_thread.setDaemon( True )
            web_server_thread.start()
            # Wait for the server to start up
            time.sleep( 3 )

            # Build the proper image URI for the call based on how the web server will be hosting it
            # TODO: Find a better way of getting your own IP address
            # socket.gethostbyname( socket.gethostname() ) returns 127.0.0.1 on many systems
            # This will open a socket with the target, and pulls the address of the socket
            groups = re.search( "^(https?)://([^:]+)(:(\d+))?$", args.rhost )
            s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
            remote_port = groups.group( 4 )
            if remote_port is None:
                remote_port = "80"
                if groups.group( 1 ) == "https":
                    remote_port = "443"
            s.connect( ( groups.group(2), int( remote_port ) ) )
            image_uri = "http://{}:{}/{}".format( s.getsockname()[0], WEB_SERVER_PORT, args.image.rsplit( os.path.sep, 1 )[-1] )
            s.close()
            response = redfish_utilities.simple_update( redfish_obj, image_uri, targets = targets )
    else:
        # Remote image; always use SimpleUpdate
        response = redfish_utilities.simple_update( redfish_obj, args.image, targets = targets )

    # Monitor the response
    print( "Update initiated..." )
    response = redfish_utilities.poll_task_monitor( redfish_obj, response )

    # Display the results
    print( "" )
    print_error_payload( response )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out and cleanup
    os.chdir( start_path )
    try:
        shutil.rmtree( WEB_SERVER_FOLDER )
    except:
        pass
    # Log out
    redfish_utilities.logout( redfish_obj )
sys.exit( exit_code )
