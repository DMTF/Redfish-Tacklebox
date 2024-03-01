# System Inventory (rf_sys_inventory.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to walk a Redfish service and list component information.

## Usage

```
usage: rf_sys_inventory.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--details] [--noabsent] [--write [WRITE]]
                           [--workaround] [--debug]

A tool to walk a Redfish service and list component information

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --details, -details   Indicates if the full details of each component should
                        be shown
  --noabsent, -noabsent
                        Indicates if absent devices should be skipped
  --write [WRITE], -w [WRITE]
                        Indicates if the inventory should be written to a
                        spreadsheet and what the file name should be if given
  --workaround, -workaround
                        Indicates if workarounds should be attempted for non-
                        conformant services
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the chassis collection for the service, and collects component information for processors, memory, drives, PCIe devices, network adapters, and storage controllers.
Using the information collected, it will build an inventory table and print the information.

Example:

```
$ rf_sys_inventory.py -u root -p root -r https://192.168.1.100 -details
'1U' Inventory
  Name                                | Description
  Chassis: 1U                         | 3500RX
                                      | Manufacturer: Contoso
                                      | Model: 3500RX
                                      | SKU: 8675309
                                      | PartNumber: 224071-J23
                                      | SerialNumber: 437XR1138R2
                                      | AssetTag: Chicago-45Z-2381
  Processor: CPU1                     | Multi-Core Intel(R) Xeon(R) processor 7xxx Series
                                      | Manufacturer: Intel(R) Corporation
                                      | Model: Multi-Core Intel(R) Xeon(R) processor 7xxx Series
  Processor: CPU2                     | Not Present
  Processor: FPGA1                    | Stratix 10
                                      | Manufacturer: Intel(R) Corporation
                                      | Model: Stratix 10
  Memory: DIMM1                       | 32768MB DDR4 DRAM
  Memory: DIMM2                       | 32768MB DDR4 DRAM
  Memory: DIMM3                       | 32768MB DDR4 DRAM
  Memory: DIMM4                       | Not Present
  Drive: SATA Bay 1                   | Contoso 7450GB Drive
                                      | Manufacturer: Contoso
                                      | Model: 3000GT8
  Drive: SATA Bay 2                   | Contoso 3725GB Drive
                                      | Manufacturer: Contoso
                                      | Model: 3000GT7
  Drive: SATA Bay 3                   | Not Present
  Drive: SATA Bay 4                   | Not Present

```
