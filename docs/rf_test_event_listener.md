# Test Event Listener (rf_test_event_listener.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to help verify a Redfish event listener.

## Usage

```
usage: rf_test_event_listener.py [-h] --listener LISTENER [--file FILE]
                                 [--id ID] [--name NAME] [--context CONTEXT]
                                 [--eventtype EVENTTYPE] [--eventid EVENTID]
                                 [--severity SEVERITY] [--message MESSAGE]
                                 [--messageid MESSAGEID]
                                 [--timestamp TIMESTAMP] [--header name value]

A tool to help verify a Redfish event listener

required arguments:
  --listener LISTENER, -l LISTENER
                        The absolute URI of the Redfish event listener (with
                        scheme)

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -file FILE
                        The filepath to a JSON file containing the event
                        payload; if this argument is specified, all other
                        arguments controlling the event data is ignored
  --id ID, -id ID       The value to specify in the Id property of the event
  --name NAME, -name NAME
                        The value to specify in the Name property of the event
  --context CONTEXT, -context CONTEXT
                        The value to specify in the Context property of the
                        event
  --eventtype EVENTTYPE, -eventtype EVENTTYPE
                        The value to specify in the EventType property of the
                        event
  --eventid EVENTID, -eventid EVENTID
                        The value to specify in the EventId property of the
                        event
  --severity SEVERITY, -severity SEVERITY
                        The value to specify in the Severity property of the
                        event
  --message MESSAGE, -message MESSAGE
                        The value to specify in the Message property of the
                        event
  --messageid MESSAGEID, -messageid MESSAGEID
                        The value to specify in the MessageId property of the
                        event
  --timestamp TIMESTAMP, -timestamp TIMESTAMP
                        The value to specify in the EventTimestamp property of
                        the event
  --header name value, -header name value
                        Name-value pairs of HTTP headers to provide with the
                        request
```

If the *file* argument is present, the payload is constructed entirely from the contents of the referenced file.
If the *file* argument is not present, all other arguments are used to build the event payload.
Once the event payload is constructed, the tool will perform a `POST` operations to the URI specified by the *listener* argument with additional HTTP headers specified by the *header* argument.

Example:

```
$ rf_test_event_listener.py -l https://redfishlistener.contoso.org
Listener responded with 204 No Content
```
