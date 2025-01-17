# Event Service (rf_event_service.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to manage the event service on a Redfish service.

## Usage

```
usage: rf_event_service.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--debug]
                           {info,subscribe,unsubscribe} ...

A tool to manage the event service on a Redfish service

positional arguments:
  {info,subscribe,unsubscribe}
    info                Displays information about the event service and
                        subscriptions
    subscribe           Creates an event subscription to a specified URL
    unsubscribe         Deletes an event subscription

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --debug               Creates debug file showing HTTP traces and exceptions
```

### Info

Displays information about the event service and subscriptions.

```
usage: rf_event_service.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the event service and event subscriptions and display their information.

Example:

```
$ rf_event_service.py -u root -p root -r https://192.168.1.100 info
Service Info
  Status: Enabled
  Delivery Retry Policy: 3 attempts, 60 second intervals
  Event Types: StatusChange, ResourceUpdated, ResourceAdded, ResourceRemoved, Alert
  Event Formats: N/A
  Registries: N/A
  Resource Types: N/A
  Include Origin of Condition Supported: False
  SSE URI: Not supported
  SSE Filter Parameters: Unknown/Unspecified

Subscription Info
  1                                    | Destination: http://www.dnsname.com/Destination1
                                       | State: Enabled
                                       | Context: WebUser3
                                       | Event Format: Event
                                       | Event Types: Alert
  2                                    | Destination: contoso_user@snmp_server.contoso.com
                                       | State: Enabled
                                       | Context: My_SNMPv3_Events
                                       | Event Format: Event
                                       | Resource Types: Certificate, Volume, Thermal, VirtualMedia, Power
  3                                    | Destination: mailto:spam@contoso.com
                                       | State: Enabled
                                       | Context: EmailUser3
                                       | Event Format: Event
                                       | Resource Types: Certificates, Systems
  4                                    | Destination: syslog://123.45.10:514
                                       | State: Enabled
                                       | Context: Syslog-Mockup
                                       | Event Format: Event
```

### Subscribe

Creates an event subscription to a specified URL.

```
usage: rf_event_service.py subscribe [-h] --destination DESTINATION
                                     [--context CONTEXT] [--expand]
                                     [--format FORMAT]
                                     [--resourcetypes RESOURCETYPES [RESOURCETYPES ...]]
                                     [--registries REGISTRIES [REGISTRIES ...]]
                                     [--eventtypes EVENTTYPES [EVENTTYPES ...]]

required arguments:
  --destination DESTINATION, -dest DESTINATION
                        The URL where events are sent for the subscription

optional arguments:
  -h, --help            show this help message and exit
  --context CONTEXT, -c CONTEXT
                        The context string for the subscription that is
                        supplied back in the event payload
  --expand, -e          Indicates if the origin of condition in the event is
                        to be expanded
  --format FORMAT, -f FORMAT
                        The format of the event payloads
  --resourcetypes RESOURCETYPES [RESOURCETYPES ...], -rt RESOURCETYPES [RESOURCETYPES ...]
                        A list of resource types for the subscription
  --registries REGISTRIES [REGISTRIES ...], -reg REGISTRIES [REGISTRIES ...]
                        A list of registries for the subscription
  --eventtypes EVENTTYPES [EVENTTYPES ...], -et EVENTTYPES [EVENTTYPES ...]
                        A list of event types for the subscription; this
                        option has been deprecated in favor of other methods
                        such as 'resource types' and 'registries'
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the event service and perform a POST operation on the event destination collection to create a new subscription.
The subscription will specify the destination to be the *destination* argument, and other optional arguments are provided as additional settings on the subscription.

Example:

```
$ rf_event_service.py -u root -p root -r https://192.168.1.100 subscribe -dest http://someremotelistener/redfish_event_handler
Created subscription '/redfish/v1/EventService/Subscriptions/5'
```

### Unsubscribe

Deletes an event subscription.

```
usage: rf_event_service.py unsubscribe [-h] --id ID

required arguments:
  --id ID, -i ID  The identifier of the event subscription to be deleted

optional arguments:
  -h, --help      show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the event service and traverse the members of the event destination collection to find a member with the `Id` property matching the *id* argument.
If a match is found, it will perform a DELETE on the member.

Example:

```
$ rf_event_service.py -u root -p root -r https://192.168.1.100 unsubscribe --id 5
Deleting subscription '5'
```
