# Boot Override (rf_boot_override.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to perform a one time boot override of a system.

## Usage

```
usage: rf_boot_override.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--system SYSTEM] [--info] [--target TARGET]
                           [--uefi UEFI] [--mode MODE] [--reset]
                           [--workaround] [--debug]

A tool to perform a one time boot override of a system

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --system SYSTEM, -s SYSTEM
                        The ID of the system to set
  --info, -info         Indicates if boot information should be reported
  --target TARGET, -t TARGET
                        The target boot device; if this argument is omitted
                        the tool will display the current boot settings
  --uefi UEFI, -uefi UEFI
                        If target is 'UefiTarget', the UEFI Device Path of the
                        device to boot. If target is 'UefiBootNext', the UEFI
                        Boot Option string of the device to boot.
  --mode MODE, -m MODE  The requested boot mode ('UEFI' or 'Legacy')
  --reset, -reset       Signifies that the system is reset after the boot
                        override is set
  --workaround, -workaround
                        Indicates if workarounds should be attempted for non-
                        conformant services
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.

* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.

The tool will then perform an operation on the `Boot` object within the matching system.

* If *target* is specified, it will update the `Boot` object to set the boot override to be *target*.
    * If *reset* is provided, it will reset the system after updating the `Boot` object.
* If *target* is not specified, it will display the current boot override settings for the system.

Example:

```
$ rf_boot_override.py -u root -p root -r https://192.168.1.100 -t Pxe -reset
Setting a one time boot for Pxe...
Resetting the system...
```
