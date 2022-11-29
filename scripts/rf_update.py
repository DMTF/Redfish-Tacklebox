#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

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
redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
redfish_obj.login( auth = "session" )

# If the file is local, spin up a web server to host the image
start_path = os.getcwd()
if os.path.isfile( args.image ):
    web_server_thread = threading.Thread( target = local_web_server, args = ( args.image, ) )
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
    s.connect( ( groups.group( 2 ), int( remote_port ) ) )
    image_uri = "http://{}:{}/{}".format( s.getsockname()[0], WEB_SERVER_PORT, args.image.rsplit( os.path.sep, 1 )[-1] )
    s.close()
else:
    image_uri = args.image

exit_code = 0
try:
    # Send the Simple Update request
    targets = None
    if args.target is not None:
        targets = [ args.target ]
    response = redfish_utilities.simple_update( redfish_obj, image_uri, targets = targets )

    # Monitor the response
    print( "Update initiated..." )
    response = redfish_utilities.poll_task_monitor( redfish_obj, response )

    # Display the results
    print( "" )
    redfish_utilities.print_error_payload( response )
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
    redfish_obj.logout()
exit( exit_code )
