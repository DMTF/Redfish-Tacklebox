# Power/Reset (rf_power_reset.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to perform a power/reset operation of a system.

## Usage

```
usage: rf_power_reset.py [-h] --user USER --password PASSWORD --rhost RHOST
                         [--system SYSTEM]
                         [--type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}]
                         [--info] [--debug]

A tool to perform a power/reset operation of a system

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --system SYSTEM, -s SYSTEM
                        The ID of the system to reset
  --type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}, -t {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}
                        The type of power/reset operation to perform
  --info, -info         Indicates if reset and power information should be
                        reported
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.
It will perform the `Reset` action with the specified reset type from the *type* argument.

* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.
* If *type* is not specified, it will attempt a `GracefulRestart`.

Example:

```
$ rf_power_reset.py -u root -p root -r https://192.168.1.100 -t GracefulRestart`
Resetting the system...
```
