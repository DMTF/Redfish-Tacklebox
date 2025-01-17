#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Raw Request

File : rf_raw_request.py

Brief : This script performs a raw request specified by the user
"""

import argparse
import json
import os
import redfish
import redfish_utilities
import sys
from redfish.messages import RedfishPasswordChangeRequiredError


def ifmatch_header(redfish_obj, path, headers=None):
    """
    Generates If-Match header for PATCH and PUT operations

    Args:
        redfish_obj: The Redfish client object with an open session
        path: The URI of the resource
        headers: Dictionary of HTTP headers to provide in the request

    Returns:
        Updated dictionary of HTTP headers with If-Match, if an ETag was found
    """

    if headers is None:
        headers = {}
    try:
        response = redfish_obj.get(path)
        etag = response.getheader("ETag")
        if etag is not None:
            headers["If-Match"] = etag
    except Exception:
        pass
    return headers


# Get the input arguments
argget = argparse.ArgumentParser(description="A tool perform a raw request to a Redfish service")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument(
    "--method",
    "-m",
    type=str,
    required=False,
    help="The HTTP method to perform; performs GET if not specified",
    default="GET",
    choices=["GET", "HEAD", "POST", "PATCH", "PUT", "DELETE"],
)
argget.add_argument("--request", "-req", type=str, required=True, help="The URI for the request")
argget.add_argument(
    "--body",
    "-b",
    type=str,
    required=False,
    help="The body to provide with the request; can be a JSON string for a JSON request, a filename to send binary data, or an unstructured string",
)
argget.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Indicates if HTTP response codes and headers are displayed",
    default=False,
)
args = argget.parse_args()

# Connect to the service
redfish_obj = None
try:
    redfish_obj = redfish.redfish_client(
        base_url=args.rhost, username=args.user, password=args.password, timeout=15, max_retry=3
    )
    redfish_obj.login(auth="session")
except RedfishPasswordChangeRequiredError:
    redfish_utilities.print_password_change_required_and_logout(redfish_obj, args)
    sys.exit(1)
except Exception:
    raise

# Encode the body
# If the body argument points to a file, load the file
if args.body is not None and os.path.isfile(args.body):
    with open(args.body, mode="rb") as file:
        body = file.read()
else:
    # Not a file; either JSON or a raw string
    try:
        body = json.loads(args.body)
    except Exception:
        body = args.body
if body is None:
    # Default case if nothing resolves (empty JSON object)
    body = {}

headers = {}
# Perform the requested operation
if args.method == "HEAD":
    resp = redfish_obj.head(args.request)
elif args.method == "POST":
    resp = redfish_obj.post(args.request, body=body)
elif args.method == "PATCH":
    headers = ifmatch_header(redfish_obj, args.request, headers=headers)
    resp = redfish_obj.patch(args.request, body=body, headers=headers)
elif args.method == "PUT":
    headers = ifmatch_header(redfish_obj, args.request, headers=headers)
    resp = redfish_obj.put(args.request, body=body, headers=headers)
elif args.method == "DELETE":
    resp = redfish_obj.delete(args.request)
else:
    resp = redfish_obj.get(args.request)

# Print HTTP status and headers
if args.verbose:
    print("HTTP {}".format(resp.status))
    for header in resp.getheaders():
        print("{}: {}".format(header[0], header[1]))
    print()

# Print the response
if resp.status != 204:
    try:
        print(json.dumps(resp.dict, sort_keys=True, indent=4, separators=(",", ": ")))
    except Exception:
        # The response is either malformed JSON or not JSON at all
        print(resp.text)
else:
    print("No response body")

# Log out
redfish_utilities.logout(redfish_obj)
sys.exit(0)
