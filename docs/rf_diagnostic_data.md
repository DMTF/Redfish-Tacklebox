# Diagnostic Data (rf_diagnostic_data.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage licenses on a Redfish service.

## Usage

```
usage: rf_diagnostic_data.py [-h] --user USER --password PASSWORD --rhost
                             RHOST [--manager [MANAGER]] [--system [SYSTEM]]
                             [--chassis [CHASSIS]] [--log LOG]
                             [--type {Manager,PreOS,OS,OEM}]
                             [--oemtype OEMTYPE] [--directory DIRECTORY]
                             [--debug]

A tool to collect diagnostic data from a log service on a Redfish service

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
  --log LOG, -l LOG     The ID of the log service
  --type {Manager,PreOS,OS,OEM}, -type {Manager,PreOS,OS,OEM}
                        The type of diagnostic data to collect; defaults to
                        'Manager' if not specified
  --oemtype OEMTYPE, -oemtype OEMTYPE
                        The OEM-specific type of diagnostic data to collect;
                        this option should only be used if the requested type
                        is 'OEM'
  --directory DIRECTORY, -d DIRECTORY
                        The directory to save the diagnostic data; defaults to
                        the current directory if not specified
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

Once the desired log service is found, the tool perform the `GetDiagnosticData` action and specify the type of diagnostic data to collect based on the *type* and *oemtype* arguments.
Once the action is complete, it will download the diagnostic data from the service and save it on the local system.

Example:

```
$ rf_diagnostic_data.py -u root -p root -r https://192.168.1.100 -m BMC
Collecting diagnostic data...
Task is Done!
Saved diagnostic data to './debug-data.tar.gz'
```
