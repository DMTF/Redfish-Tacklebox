# Update (rf_update.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to perform an update with a Redfish service.

## Usage

```
usage: rf_update.py [-h] --user USER --password PASSWORD --rhost RHOST --image
                    IMAGE [--target TARGET]
                    [--applytime {Immediate,OnReset,AtMaintenanceWindowStart,InMaintenanceWindowOnReset,OnStartUpdateRequest}]
                    [--timeout TIMEOUT] [--debug]

A tool to perform an update with a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)
  --image IMAGE, -i IMAGE
                        The URI or filepath of the image

optional arguments:
  -h, --help            show this help message and exit
  --target TARGET, -t TARGET
                        The target resource to apply the image
  --applytime {Immediate,OnReset,AtMaintenanceWindowStart,InMaintenanceWindowOnReset,OnStartUpdateRequest}, -at {Immediate,OnReset,AtMaintenanceWindowStart,InMaintenanceWindowOnReset,OnStartUpdateRequest}
                        The apply time for the update
  --timeout TIMEOUT, -timeout TIMEOUT
                        The timeout, in seconds, to transfer the image; by
                        default this is 2 seconds per MB
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then builds a request payload to perform a `SimpleUpdate` action against the update service using the image specified by the *image* argument.
The optional *target* argument is used in the request if attempting to update a particular system, device, manager, or other resource.
Once the `SimpleUpdate` is requested, it monitors the progress of the update, and displays response messages reported by the service about the update once complete.

Example:

```
$ rf_update.py -u root -p root -r https://192.168.1.100 -i image.bin

Pushing the image to the service directly; depending on the size of the image, this can take a few minutes...
Update initiated...
Task is Done!

Success
```
