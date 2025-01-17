# BIOS Settings (rf_bios_settings.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manager BIOS settings for a system.

## Usage

```
usage: rf_bios_settings.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--system SYSTEM] [--attribute name value]
                           [--reset] [--workaround] [--debug]

A tool to manager BIOS settings for a system

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --system SYSTEM, -s SYSTEM
                        The ID of the system to manage
  --attribute name value, -a name value
                        Sets a BIOS attribute to a new value; can be supplied
                        multiple times to set multiple attributes
  --reset, -reset       Resets BIOS to the default settings
  --workaround, -workaround
                        Indicates if workarounds should be attempted for non-
                        conformant services
  --debug               Creates debug file showing HTTP traces and exception
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.

* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.

The tool will then get the BIOS resource for the matching system.

* If *reset* is specified, it will perform a request to set BIOS to the default settings.
* If *attribute* is specified, it will update the BIOS resource with the new attribute value.
* Otherwise, it will display the BIOS settings.

Example; display attributes:

```
$ rf_bios_settings.py -u root -p root -r https://192.168.1.100

BIOS Settings:
  Attribute Name                 | Current Setting                | Future Setting                
  AdminPhone                     |                                | (404) 555-1212                
  BootMode                       | Uefi                           | Uefi                          
  EmbeddedSata                   | Raid                           | Ahci                          
  NicBoot1                       | NetworkBoot                    | NetworkBoot                   
  NicBoot2                       | Disabled                       | NetworkBoot                   
  PowerProfile                   | MaxPerf                        | MaxPerf                       
  ProcCoreDisable                | 0                              | 0                             
  ProcHyperthreading             | Enabled                        | Enabled                       
  ProcTurboMode                  | Enabled                        | Disabled                      
  UsbControl                     | UsbEnabled                     | UsbEnabled                    

```

Example; set an attribute:

```
$ rf_bios_settings.py -u root -p root -r https://192.168.1.100 -a BiosMode Legacy
Setting BiosMode to Legacy...
```

Example; reset BIOS to the default settings:

```
$ rf_bios_settings.py -u root -p root -r https://192.168.1.100 -reset
Resetting the BIOS settings...
```
