# Logs (rf_logs.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to manage the SEL on a Redfish service.

## Usage

```
usage: rf_sel.py [-h] --user USER --password PASSWORD --rhost RHOST
                 [--details] [--clear] [--debug]

A tool to manage the SEL on a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --details, -details   Indicates details to be shown for each log entry
  --clear, -clear       Indicates if the log should be cleared
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then attempt to locate the SEL via the following logic:

* It will iterate through each log service found in each manager.
* The first log service found where `LogEntryType` contains `SEL` is considered the SEL for the service.

Once the SEL is found, the tool will either perform the `ClearLog` action if *clear* is provided, or read and display the log entries.

Example:

```
$ rf_sel.py -u root -p root -r https://192.168.1.100
  Id    | Timestamp                 | Message
  1     | 2012-03-07T14:44:00Z      | System May be Melting
```
