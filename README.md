# Redfish Tackebox

Copyright 2019 DMTF. All rights reserved.

## About

Redfish Tacklebox contains a set of Python utilities to perform common management operations with a Redfish service.  The utilities can be used as part of larger management applications, or be used as standalone command line tools.


## Requirements

Ensure that the machine has Python3 installed.

External modules:
* redfish: https://pypi.python.org/pypi/redfish

You may install the external modules by running:

`pip3 install -r requirements.txt`


## Utilities


### Sensor List

```
usage: sensor_list.py [-h] --user USER --password PASSWORD --rhost RHOST

A tool to walk a Redfish service and list sensor info

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
```

Example: `python3 sensor_list.py -u <user> -p <password> -r <rhost>`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.  It then traverses the Chassis Collection for the Service, and reads their respective Power and Thermal Resources.  Using the information from those resources, it will build a sensor table and print the information collected.
