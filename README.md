# Redfish Tacklebox

Copyright 2019 DMTF. All rights reserved.

## About

Redfish Tacklebox contains a set of Python utilities to perform common management operations with a Redfish service.
The utilities can be used as part of larger management applications, or be used as standalone command line tools.

## Installation

`pip install redfish_utilities`


### Building from Source

```
python setup.py sdist --formats=zip
cd dist
pip install redfish_utilities-x.x.x.zip
```


## Requirements

External modules:
* redfish: https://pypi.python.org/pypi/redfish

You may install the external modules by running:

`pip install -r requirements.txt`


## Utilities


### Discover

```
usage: rf_discover.py [-h]

A tool to discover Redfish services

optional arguments:
  -h, --help  show this help message and exit
```

Example: `rf_discover.py`

The tool will perform an SSDP request to find all available Redfish services.
Once all of the responses are collected, it will print each service with its UUID and service root.


### Sensor List

```
usage: rf_sensor_list.py [-h] --user USER --password PASSWORD --rhost RHOST

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

Example: `rf_sensor_list.py -u root -p root -r https://192.168.1.100`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the chassis collection for the service, and reads their respective power and thermal resources.
Using the information from those resources, it will build a sensor table and print the information collected.


### System Inventory

```
usage: rf_sys_inventory.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--details] [--noabsent]

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
```

Example: `rf_sys_inventory.py -u root -p root -r https://192.168.1.100 -details`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the chassis collection for the service, and collects component information for processors, memory, drives, PCIe devices, network adapters, and storage controllers.
Using the information collected, it will build an inventory table and print the information.


### Logs

```
usage: rf_logs.py [-h] --user USER --password PASSWORD --rhost RHOST
                  [--manager [MANAGER]] [--system [SYSTEM]]
                  [--chassis [CHASSIS]] [--log LOG] [--details] [--clear]

A tool to manage logs on a Redfish service

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
  --log LOG, -l LOG     The ID of the resource containing the log service
  --details, -details   Indicates details to be shown for each log entry
  --clear, -clear       Indicates if the log should be cleared
```

Example: `rf_logs.py -u root -p root -r https://192.168.1.100 -m BMC`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then attempt to locate the appropriate log service via the following logic:
* If the *manager* argument is provided, it will traverse the manager collection for the matching manager.
* If the *system* argument is provided, it will traverse the system collection for the matching system.
* If the *chassis* argument is provided, it will traverse the chassis collection for the matching chassis.
* If any of the above arguments are provided without a specified Id, but the collection contains exactly one member, then that member is used.
* If none of the above arguments are provided, then the tool will try to use a manager in the manager collection if there is only one member present.
* Within the member, the tool will find the matching log service based on the *log* argument.
    * If *log* is not specified, and there is exactly one log service in the member, then the tool will use that one log service.

Once the desired log service is found, the tool will either perform the `ClearLog` action if *clear* is provided, or read and display the log entries.


### Power/Reset

```
usage: rf_power_reset.py [-h] --user USER --password PASSWORD --rhost RHOST
                         [--system SYSTEM] [--type TYPE]

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
                        The ID of the system perform the operation
  --type TYPE, -t TYPE  The type of power/reset operation to perform
  --info, -info         Indicates if reset information should be reported
```

Example: `rf_power_reset.py -u root -p root -r https://192.168.1.100 -t GracefulRestart`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.
It will perform the `Reset` action with the specified reset type from the *type* argument.
* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.
* If *type* is not specified, it will attempt a `GracefulRestart`.


### Boot Override

```
usage: rf_boot_override.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--system SYSTEM] [--target TARGET] [--uefi UEFI]
                           [--reset]

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
  --target TARGET, -t TARGET
                        The target boot device; if not provided the tool will
                        display the current boot settings
  --uefi UEFI, -uefi UEFI
                        If target is 'UefiTarget', the UEFI Device Path of the
                        device to boot. If target is 'UefiBootNext', the UEFI
                        Boot Option string of the device to boot.
  --reset, -reset       Signifies that the system is reset after the boot
                        override is set
```

Example: `rf_boot_override.py -u root -p root -r https://192.168.1.100 -t Pxe -reset`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.
* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.

The tool will then perform an operation on the `Boot` object within the matching system.
* If *target* is specified, it will update the `Boot` object to set the boot override to be *target*.
    * If *reset* is provided, it will reset the system after updating the `Boot` object.
* If *target* is not specified, it will display the current boot override settings for the system.


### Accounts

```
usage: rf_accounts.py [-h] --user USER --password PASSWORD --rhost RHOST
                      [--add name password role] [--delete DELETE]
                      [--setname old_name new_name]
                      [--setpassword name new_password]
                      [--setrole name new_role] [--enable ENABLE]
                      [--disable DISABLE] [--unlock UNLOCK]

A tool to manage user accounts on a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --add name password role, -add name password role
                        Adds a new user account
  --delete DELETE, -delete DELETE
                        Deletes a user account with the given name
  --setname old_name new_name, -setname old_name new_name
                        Sets a user account to a new name
  --setpassword name new_password, -setpassword name new_password
                        Sets a user account to a new password
  --setrole name new_role, -setrole name new_role
                        Sets a user account to a new role
  --enable ENABLE, -enable ENABLE
                        Enables a user account with the given name
  --disable DISABLE, -disable DISABLE
                        Disabled a user account with the given name
  --unlock UNLOCK, -unlock UNLOCK
                        Unlocks a user account with the given name
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
Based on the parameters, it will display, add, delete, or modify user accounts.
* The *add* argument is used to create a new user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -add new_name new_password new_role`
* The *delete* argument is used to delete a user account based on the given user name
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -delete user_to_delete`
* The *setname* argument is used to change the name of a user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -setname user_to_change new_name`
* The *setpassword* argument is used to change the password of a user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -setpassword user_to_change new_password`
* The *setrole* argument is used to change the role of a user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -setrole user_to_change new_role`
* The *enable* argument is used to enable a user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -enable user_to_change`
* The *disable* argument is used to disable a user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -disable user_to_change`
* The *unlock* argument is used to unlock a user account
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100 -unlock user_to_change`
* If none of the above arguments are given, a table of the user accounts is provided
    * Example: `rf_accounts.py -u root -p root -r https://192.168.1.100`


### Update

```
usage: rf_update.py [-h] --user USER --password PASSWORD --rhost RHOST --image
                    IMAGE [--target TARGET]

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
```

Example: `rf_update.py -u root -p root -r https://192.168.1.100 -i image.bin`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then builds a request payload to perform a `SimpleUpdate` action against the update service using the image specified by the *image* argument.
The optional *target* argument is used in the request if attempting to update a particular system, device, manager, or other resource.
Once the `SimpleUpdate` is requested, it monitors the progress of the update, and displays response messages reported by the service about the update once complete.


## Release Process

1. Update `CHANGELOG.md` with the list of changes since the last release
2. Update `setup.py` to reflect the new version
3. Push changes to Github and create a new release
4. Push the new tool version to pypi.org
    * `python setup.py sdist`
    * `twine upload dist/*`
