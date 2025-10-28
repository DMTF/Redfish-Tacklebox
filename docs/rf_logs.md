# Logs (rf_logs.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to manage logs on a Redfish service.

## Usage

```
usage: rf_logs.py [-h] --user USER --password PASSWORD --rhost
                  RHOST [--manager [MANAGER]]
                  [--system [SYSTEM]] [--chassis [CHASSIS]]
                  [--log LOG] [--first FIRST] [--max MAX]
                  [--starttime STARTTIME] [--endtime ENDTIME]
                  [--details] [--clear] [--debug]

A tool to manage logs on a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --manager [MANAGER], -m [MANAGER]
                        The ID of the manager containing the log service
  --system [SYSTEM], -s [SYSTEM]
                        The ID of the system containing the log service
  --chassis [CHASSIS], -c [CHASSIS]
                        The ID of the chassis containing the log service
  --log LOG, -l LOG     The ID of the resource containing the log service
  --first FIRST, -first FIRST
                        The index of the first log entry to
                        collect
  --max MAX, -max MAX   The maximum number of log entries to
                        collect
  --starttime STARTTIME, -start STARTTIME
                        The timestamp of the oldest log entry
                        to collect in ISO8601 date-time format
  --endtime ENDTIME, -end ENDTIME
                        The timestamp of the newest log entry
                        to collect in ISO8601 date-time format
  --details, -details   Indicates details to be shown for each log entry
  --clear, -clear       Indicates if the log should be cleared
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then attempt to locate the appropriate log service via the following logic:

* If the *manager* argument is provided, it will traverse the manager collection for the matching manager.
* If the *system* argument is provided, it will traverse the system collection for the matching system.
* If the *chassis* argument is provided, it will traverse the chassis collection for the matching chassis.
* If any of the above arguments are provided without a specified Id, but the collection contains exactly one member, then that member is used.
* If none of the above arguments are provided, then the tool will try to use a manager in the manager collection if there is only one member present.
* Within the member, the tool will find the matching log service based on the *log* argument.
    * If *log* is not specified, and there is exactly one log service in the member, then the tool will use that one log service.

Once the desired log service is found, the tool will either perform the `ClearLog` action if *clear* is provided, or read and display the log entries.
If displaying the log entries, it will apply the filters and restrictions specified by the *first*, *max*, *starttime*, and *endtime* arguments.

Example:

```
$ rf_logs.py -u root -p root -r https://192.168.1.100 -m BMC
  Id    | Timestamp                 | Message
  1     | 2012-03-07T14:44:00Z      | System May be Melting
```
