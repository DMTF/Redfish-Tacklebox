# Firmware Inventory (rf_firmware_inventory.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to collect firmware inventory from a Redfish service.

## Usage

```
usage: rf_firmware_inventory.py [-h] --user USER --password PASSWORD --rhost
                                RHOST [--details] [--id] [--debug]

A tool to collect firmware inventory from a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --details, -details   Indicates details to be shown for each firmware entry
  --id, -i              Construct inventory names using 'Id' values
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then retrieves the firmware inventory collection under the update service and prints its contents.

Example:

```
$ rf_firmware_inventory.py -u root -p root -r https://192.168.1.100 -details 
  Contoso BMC Firmware                     | Version: 1.45.455b66-rev4
                                           | Manufacturer: Contoso
                                           | SoftwareId: 1624A9DF-5E13-47FC-874A-DF3AFF143089
                                           | ReleaseDate: 2017-08-22T12:00:00Z
  Contoso Simple Storage Firmware          | Version: 2.50
                                           | Manufacturer: Contoso
                                           | ReleaseDate: 2021-10-18T12:00:00Z
  Contoso BIOS Firmware                    | Version: P79 v1.45
                                           | Manufacturer: Contoso
                                           | SoftwareId: FEE82A67-6CE2-4625-9F44-237AD2402C28
                                           | ReleaseDate: 2017-12-06T12:00:00Z

```
