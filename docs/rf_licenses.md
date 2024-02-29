# Licenses (rf_licenses.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage licenses on a Redfish service.

## Usage

```
usage: rf_licenses.py [-h] --user USER --password PASSWORD --rhost RHOST
                      [--debug]
                      {info,install,delete} ...

A tool to manage licenses on a Redfish service

positional arguments:
  {info,install,delete}
    info                Displays information about the licenses installed on
                        the service
    install             Installs a new license
    delete              Deletes a license

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --debug               Creates debug file showing HTTP traces and exceptions
```

### Info

Displays information about the licenses installed on the service.

```
usage: rf_licenses.py info [-h] [--details]

optional arguments:
  -h, --help           show this help message and exit
  --details, -details  Indicates if the full details of each license should be
                       shown
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the license service, find its license collection, and display the licenses.

Example:

```
$ rf_licenses.py -u root -p root -r https://192.168.1.100 info

  License                        | Details
  RemotePresence                 | LIC023923978, Installed on 2023-08-20T20:13:44Z, Expires on 2026-08-20T20:13:43Z
  RedfishTelemetry               | LIC892345871, Installed on 2023-04-21T08:44:02Z, Installed on 2026-04-21T08:44:02Z

```

### Install

Installs a new license.

```
usage: rf_licenses.py install [-h] --license LICENSE

required arguments:
  --license LICENSE, -l LICENSE
                        The filepath or URI to the license to install

optional arguments:
  -h, --help            show this help message and exit
``` 

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the license service.
If the license referenced by the *license* argument is local file, it will insert the contents of the license file in the license collection.
Otherwise, it will install the new license with the `Install` action found on the license service.

Example:

```
$ rf_licenses.py -u root -p root -r https://192.168.1.100 install --license /home/user/my_license.xml
Installing license '/home/user/my_license.xml'...
```

### Delete

Deletes a license.

```
usage: rf_licenses.py delete [-h] --license LICENSE

required arguments:
  --license LICENSE, -l LICENSE
                        The identifier of the license to delete

optional arguments:
  -h, --help            show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the license service and find the license requested by the *license* argument.
If the matching license is found, it will delete the license.

Example:

```
$ rf_licenses.py -u root -p root -r https://192.168.1.100 delete --license 1
Deleting license '1'...
```
