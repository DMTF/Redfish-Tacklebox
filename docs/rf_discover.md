# Discover (rf_discover.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to discover Redfish services.

## Usage

```
usage: rf_discover.py [-h]

A tool to discover Redfish services

optional arguments:
  -h, --help  show this help message and exit
```

The tool will perform an SSDP request to find all available Redfish services.
Once all the responses are collected, it will print each service with its UUID and service root.

Example:

```
$ rf_discover.py
Redfish services:
5822e6cd-35e1-45ab-99de-797bc78edf48: https://192.168.1.17/redfish/v1/
03fff361-3520-421f-9511-71b97093cb79: https://192.168.1.22/redfish/v1/
b010f703-7c4e-441b-bb77-aad212d897d2: https://192.168.1.70/redfish/v1/
a3dd7e36-c96c-473d-858a-bdfa7fa5cdd7: https://192.168.1.18/redfish/v1/
5d23dd1c-dfd8-4b83-963f-ec3e7c1c8b27: https://192.168.1.96/redfish/v1/
```
