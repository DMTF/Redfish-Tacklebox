#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Test Event Listener

File : rf_test_event_listener.py

Brief : This script performs POST operations with event payloads to help verify
        an event listener.
"""

import argparse
import json
import requests
from datetime import datetime

event_headers = {"Content-Type": "application/json"}

event_payload = {
    "@odata.type": "#Event.v1_7_0.Event",
    "Id": "1",
    "Name": "Sample Event",
    "Context": "Sample Event for Listener",
    "Events": [
        {
            "EventType": "Other",
            "EventId": "1",
            "Severity": "OK",
            "MessageSeverity": "OK",
            "Message": "Test message.",
            "MessageId": "Resource.1.3.TestMessage",
        }
    ],
}

argget = argparse.ArgumentParser(description="A tool to help verify a Redfish event listener")
argget.add_argument(
    "--listener", "-l", type=str, required=True, help="The absolute URI of the Redfish event listener (with scheme)"
)
argget.add_argument(
    "--file",
    "-file",
    type=str,
    help="The filepath to a JSON file containing the event payload; if this argument is specified, all other arguments controlling the event data is ignored",
)
argget.add_argument("--id", "-id", type=str, help="The value to specify in the Id property of the event")
argget.add_argument("--name", "-name", type=str, help="The value to specify in the Name property of the event")
argget.add_argument("--context", "-context", type=str, help="The value to specify in the Context property of the event")
argget.add_argument(
    "--eventtype", "-eventtype", type=str, help="The value to specify in the EventType property of the event"
)
argget.add_argument("--eventid", "-eventid", type=str, help="The value to specify in the EventId property of the event")
argget.add_argument(
    "--severity", "-severity", type=str, help="The value to specify in the Severity property of the event"
)
argget.add_argument("--message", "-message", type=str, help="The value to specify in the Message property of the event")
argget.add_argument(
    "--messageid", "-messageid", type=str, help="The value to specify in the MessageId property of the event"
)
argget.add_argument(
    "--timestamp", "-timestamp", type=str, help="The value to specify in the EventTimestamp property of the event"
)
argget.add_argument(
    "--header",
    "-header",
    type=str,
    nargs=2,
    metavar=("name", "value"),
    action="append",
    help="Name-value pairs of HTTP headers to provide with the request",
)
args = argget.parse_args()

# Update the event payload based on the specified arguments
if args.file:
    with open(args.file) as json_file:
        event_payload = json.load(json_file)
else:
    if args.id:
        event_payload["Id"] = args.id
    if args.name:
        event_payload["Name"] = args.name
    if args.context:
        event_payload["Context"] = args.context
    if args.eventtype:
        event_payload["Events"][0]["EventType"] = args.eventtype
    if args.eventid:
        event_payload["Events"][0]["EventId"] = args.eventid
    if args.severity:
        event_payload["Events"][0]["Severity"] = args.severity
        event_payload["Events"][0]["MessageSeverity"] = args.severity
    if args.message:
        event_payload["Events"][0]["Message"] = args.message
    if args.messageid:
        event_payload["Events"][0]["MessageId"] = args.messageid
    if args.timestamp:
        event_payload["Events"][0]["EventTimestamp"] = args.timestamp
    else:
        event_payload["Events"][0]["EventTimestamp"] = datetime.now().replace(microsecond=0).astimezone().isoformat()

# Update the HTTP headers based on the specified arguments
if args.header:
    for header in args.header:
        event_headers[header[0]] = header[1]

# Send the request
response = requests.post(args.listener, json=event_payload, headers=event_headers, timeout=15, verify=False)
print("Listener responded with {} {}".format(response.status_code, response.reason))
