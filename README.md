# Redfish Tacklebox

Copyright 2019-2022 DMTF. All rights reserved.

## About

Redfish Tacklebox contains a set of Python3 utilities to perform common management operations with a Redfish service.
The utilities can be used as part of larger management applications, or be used as standalone command line tools.

## Installation

`pip install redfish_utilities`


### Building from Source

```
python setup.py sdist
pip install dist/redfish_utilities-x.x.x.tar.gz
```


## Requirements

External modules:
* redfish: https://pypi.python.org/pypi/redfish
* XlsxWriter: https://pypi.org/project/XlsxWriter

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
Once all the responses are collected, it will print each service with its UUID and service root.


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
  --id, -i              Construct sensor names using 'Id' values
  --name, -n            Construct sensor names using 'Name' values
  --debug               Creates debug file showing HTTP traces and exceptions
```

Example: `rf_sensor_list.py -u root -p root -r https://192.168.1.100`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the chassis collection for the service, and reads their respective power and thermal resources.
Using the information from those resources, it will build a sensor table and print the information collected.


### System Inventory

```
usage: rf_sys_inventory.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--details] [--noabsent] [--write [WRITE]]

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
  --debug               Creates debug file showing HTTP traces and exceptions
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
                         [--system SYSTEM]
                         [--type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}]
                         [--info]

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

Example: `rf_boot_override.py -u root -p root -r https://192.168.1.100 -t Pxe -reset`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.
* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.

The tool will then perform an operation on the `Boot` object within the matching system.
* If *target* is specified, it will update the `Boot` object to set the boot override to be *target*.
    * If *reset* is provided, it will reset the system after updating the `Boot` object.
* If *target* is not specified, it will display the current boot override settings for the system.


### Manager Configuration

```
usage: rf_manager_config.py [-h] --user USER --password PASSWORD --rhost RHOST
                            [--manager MANAGER]
                            {info,reset,getnet,setnet,resettodefaults,settime}
                            ...

A tool to manage managers in a service

positional arguments:
  {info,reset,getnet,setnet,resettodefaults,settime}
    info                Displays information about a manager
    reset               Resets a manager
    getnet              Displays information about an Ethernet interface
    setnet              Configures an Ethernet interface
    resettodefaults     Resets a manager to default settings
    settime             Sets the date-time on a manager

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --manager MANAGER, -m MANAGER
                        The ID of the manager to target
  --debug               Creates debug file showing HTTP traces and exceptions
```


#### Info

```
usage: rf_manager_config.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 info`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, and displays the manager instance.
* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.


#### Reset

```
usage: rf_manager_config.py reset [-h]
                                  [--type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle}]
                                  [--info]

optional arguments:
  -h, --help            show this help message and exit
  --type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle}, -t {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle}
                        The type of power/reset operation to perform
  --info, -info         Indicates if reset information should be reported
```

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 reset -t GracefulRestart`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the manager collection for the service to find the matching manager specified by the *manager* argument.
It will perform the `Reset` action with the specified reset type from the *type* argument.
* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *type* is not specified, it will attempt a `GracefulRestart`.


#### Set Time

```
usage: rf_manager_config.py settime [-h] [--datetime DATETIME] [--offset OFFSET]

optional arguments:
  -h, --help            show this help message and exit
  --datetime DATETIME, -dt DATETIME
                        The date-time value to set
  --offset OFFSET, -o OFFSET
                        The date-time offset value to set
```

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 settime -dt 2023-07-27T12:00:00-05:00`

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 settime -o=-05:00`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, and applies the *datetime* and *offset* values to the manager instance.
* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.


#### Get Network Interface

```
usage: rf_manager_config.py getnet [-h] [--id ID]

optional arguments:
  -h, --help      show this help message and exit
  --id ID, -i ID  The identifier of the Ethernet interface to display
```

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 getnet -i NIC2`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, locate the Ethernet interface specified by the *id* argument, and displays the interface instance.
* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *id* is not specified, and if the manager has exactly one Ethernet interface, it will perform the operation on the one interface.


#### Set Network Interface

```
usage: rf_manager_config.py setnet [-h] [--id ID] [--ipv4address IPV4ADDRESS]
                                   [--ipv4netmask IPV4NETMASK]
                                   [--ipv4gateway IPV4GATEWAY]
                                   [--dhcpv4 {On,Off}]
                                   [--ipv6addresses IPV6ADDRESSES [IPV6ADDRESSES ...]]
                                   [--ipv6gateways IPV6GATEWAYS [IPV6GATEWAYS ...]]
                                   [--dhcpv6 {Stateful,Stateless,Disabled,Enabled}]
                                   [--vlan {On,Off}] [--vlanid VLANID]
                                   [--vlanpriority VLANPRIORITY]

optional arguments:
  -h, --help            show this help message and exit
  --id ID, -i ID        The identifier of the Ethernet interface to configure
  --ipv4address IPV4ADDRESS, -ipv4address IPV4ADDRESS
                        The static IPv4 address to set
  --ipv4netmask IPV4NETMASK, -ipv4netmask IPV4NETMASK
                        The static IPv4 subnet mask to set
  --ipv4gateway IPV4GATEWAY, -ipv4gateway IPV4GATEWAY
                        The static IPv4 gateway to set
  --dhcpv4 {On,Off}, -dhcpv4 {On,Off}
                        The DHCPv4 configuration to set
  --ipv6addresses IPV6ADDRESSES [IPV6ADDRESSES ...], -ipv6addresses IPV6ADDRESSES [IPV6ADDRESSES ...]
                        The static IPv6 addresses to set with prefix length
  --ipv6gateways IPV6GATEWAYS [IPV6GATEWAYS ...], -ipv6gateways IPV6GATEWAYS [IPV6GATEWAYS ...]
                        The static IPv6 default gateways to set with prefix
                        length
  --dhcpv6 {Stateful,Stateless,Disabled,Enabled}, -dhcpv6 {Stateful,Stateless,Disabled,Enabled}
                        The DHCPv6 configuration to set
  --vlan {On,Off}, -vlan {On,Off}
                        The VLAN enabled configuration to set
  --vlanid VLANID, -vlanid VLANID
                        The VLAN ID to set
  --vlanpriority VLANPRIORITY, -vlanpriority VLANPRIORITY
                        The VLAN priority to set
```

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 setnet -i NIC2 -ipv4address 192.168.1.101 -ipv4gateway 192.168.1.1`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, locate the Ethernet interface specified by the *id* argument, and apply the requested settings to the interface.
* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *id* is not specified, and if the manager has exactly one Ethernet interface, it will perform the operation on the one interface.


#### Reset to Defaults

```
usage: rf_manager_config.py resettodefaults [-h]
                                            [--type {ResetAll,PreserveNetworkAndUsers,PreserveNetwork}]
                                            [--info]

optional arguments:
  -h, --help            show this help message and exit
  --type {ResetAll,PreserveNetworkAndUsers,PreserveNetwork}, -t {ResetAll,PreserveNetworkAndUsers,PreserveNetwork}
                        The type of reset-to-defaults operation to perform
  --info, -info         Indicates if reset-to-defaults information should be
                        reported
```

Example: `rf_manager_config.py -u root -p root -r https://192.168.1.100 resettodefaults -t ResetAll`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the manager collection for the service to find the matching system specified by the *manager* argument.
It will perform the `ResetToDefaults` action with the specified reset type from the *type* argument.
* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *type* is not specified, it will attempt to perform the action with `PreserveNetworkAndUsers`.


### BIOS Settings

```
usage: rf_bios_settings.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--system SYSTEM] [--attribute name value]

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
  --workaround, -workaround
                        Indicates if workarounds should be attempted for non-
                        conformant services
  --debug               Creates debug file showing HTTP traces and exceptions
```

Example: `rf_bios_settings.py -u root -p root -r https://192.168.1.100 -a BiosMode Legacy`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the system collection for the service to find the matching system specified by the *system* argument.
* If *system* is not specified, and if the service has exactly one system, it will perform the operation on the one system.

The tool will then get the BIOS resource for the matching system.
* If *attribute* is specified, it will update the BIOS resource with the new attribute value.
* If *attribute* is not specified, it will display the BIOS settings.


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
  --debug               Creates debug file showing HTTP traces and exceptions
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
  --debug               Creates debug file showing HTTP traces and exceptions
```

Example: `rf_update.py -u root -p root -r https://192.168.1.100 -i image.bin`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then builds a request payload to perform a `SimpleUpdate` action against the update service using the image specified by the *image* argument.
The optional *target* argument is used in the request if attempting to update a particular system, device, manager, or other resource.
Once the `SimpleUpdate` is requested, it monitors the progress of the update, and displays response messages reported by the service about the update once complete.


### Event Service

```
usage: rf_event_service.py [-h] --user USER --password PASSWORD --rhost RHOST
                           {subscribe,unsubscribe,info} ...

A tool to manage the event service on a Redfish service

positional arguments:
  {info,subscribe,unsubscribe}
    info                Displays information about the event service and
                        subscriptions
    subscribe           Creates an event subscription to a specified URL
    unsubscribe         Deletes an event subscription

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


#### Info

```
usage: rf_event_service.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

Example: `rf_event_service.py -u root -p root -r https://192.168.1.100 info`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the event service and event subscriptions and display their information.


#### Subscribe

```
usage: rf_event_service.py subscribe [-h] --destination DESTINATION
                                     [--context CONTEXT] [--expand]
                                     [--format FORMAT]
                                     [--resourcetypes RESOURCETYPES [RESOURCETYPES ...]]
                                     [--registries REGISTRIES [REGISTRIES ...]]

required arguments:
  --destination DESTINATION, -dest DESTINATION
                        The URL where events are sent for the subscription

optional arguments:
  -h, --help            show this help message and exit
  --context CONTEXT, -c CONTEXT
                        The context string for the subscription that is
                        supplied back in the event payload
  --expand, -e          Indicates if the origin of condition in the event is
                        to be expanded
  --format FORMAT, -f FORMAT
                        The format of the event payloads
  --resourcetypes RESOURCETYPES [RESOURCETYPES ...], -rt RESOURCETYPES [RESOURCETYPES ...]
                        A list of resource types for the subscription
  --registries REGISTRIES [REGISTRIES ...], -reg REGISTRIES [REGISTRIES ...]
                        A list of registries for the subscription
  --eventtypes EVENTTYPES [EVENTTYPES ...], -et EVENTTYPES [EVENTTYPES ...]
                        A list of event types for the subscription; this
                        option has been deprecated in favor of other methods
                        such as 'resource types' and 'registries'
``` 

Example: `rf_event_service.py -u root -p root -r https://192.168.1.100 subscribe -dest http://someremotelistener/redfish_event_handler`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the event service and perform a POST operation on the event destination collection to create a new subscription.
The subscription will specify the destination to be the *destination* argument, and other optional arguments are provided as additional settings on the subscription.


#### Unsubscribe

```
usage: rf_event_service.py unsubscribe [-h] --id ID

required arguments:
  --id ID, -i ID  The identifier of the event subscription to be deleted

optional arguments:
  -h, --help      show this help message and exit
```

Example: `rf_event_service.py -u root -p root -r https://192.168.1.100 unsubscribe --id 1`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the event service and traverse the members of the event destination collection to find a member with the `Id` property matching the *id* argument.
If a match is found, it will perform a DELETE on the member.


### Virtual Media

```
usage: rf_virtual_media.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--system SYSTEM]
                           {info,insert,eject} ...

A tool to manage virtual media of a system

positional arguments:
  {info,insert,eject}
    info                Displays information about the virtual media for a
                        system
    insert              Inserts virtual media for a system
    eject               Ejects virtual media from a system

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --system SYSTEM, -s SYSTEM
                        The ID of the system containing the virtual media
  --debug               Creates debug file showing HTTP traces and exceptions
```


#### Info

```
usage: rf_virtual_media.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

Example: `rf_virtual_media.py -u root -p root -r https://192.168.1.100 info`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the system specified by the *system* argument, find its virtual media collection, and display the virtual media instances.


#### Insert

```
usage: rf_virtual_media.py insert [-h] --image IMAGE [--id ID] [--notinserted]
                                  [--writable]
                                  [--mediatypes MEDIATYPES [MEDIATYPES ...]]

required arguments:
  --image IMAGE, -image IMAGE
                        The URI of the image to insert

optional arguments:
  -h, --help            show this help message and exit
  --id ID, -i ID        The identifier of the virtual media instance to insert
  --notinserted, -notinserted
                        Indicates if the media is to be marked as not inserted
                        for the system
  --writable, -writable
                        Indicates if the media is to be marked as writable for
                        the system
  --mediatypes MEDIATYPES [MEDIATYPES ...], -mt MEDIATYPES [MEDIATYPES ...]
                        A list of acceptable media types for the virtual media
``` 

Example: `rf_virtual_media.py -u root -p root -r https://192.168.1.100 insert -image http://somefileserver/my_media.iso`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the system specified by the *system* argument, find its virtual media collection.
It will then iterate through the virtual media collection, and insert the virtual media specified by the *image* argument in an appropriate slot.


#### Eject

```
usage: rf_virtual_media.py eject [-h] --id ID

required arguments:
  --id ID, -i ID  The identifier of the virtual media instance to eject

optional arguments:
  -h, --help      show this help message and exit
```

Example: `rf_virtual_media.py -u root -p root -r https://192.168.1.100 eject --id 1`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the system specified by the *system* argument, find its virtual media collection.
It will then locate the virtual media instance with matching `Id` property with the *id* argument, and then eject the media.


### Licenses

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


#### Info

```
usage: rf_licenses.py info [-h] [--details]

optional arguments:
  -h, --help           show this help message and exit
  --details, -details  Indicates if the full details of each license should be
                       shown
```

Example: `rf_licenses.py -u root -p root -r https://192.168.1.100 info`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the license service, find its license collection, and display the licenses.


#### Install

```
usage: rf_licenses.py install [-h] --license LICENSE

required arguments:
  --license LICENSE, -l LICENSE
                        The filepath or URI to the license to install

optional arguments:
  -h, --help            show this help message and exit
``` 

Example: `rf_licenses.py -u root -p root -r https://192.168.1.100 install --license /home/user/my_license.xml`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the license service.
If the license referenced by the *license* argument is local file, it will insert the contents of the license file in the license collection.
Otherwise, it will install the new license with the `Install` action found on the license service.


#### Delete

```
usage: rf_licenses.py delete [-h] --license LICENSE

required arguments:
  --license LICENSE, -l LICENSE
                        The identifier of the license to delete

optional arguments:
  -h, --help            show this help message and exit
```

Example: `rf_licenses.py -u root -p root -r https://192.168.1.100 delete --license 1`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the license service and find the license requested by the *license* argument.
If the matching license is found, it will delete the license.


### Certificates

```
usage: rf_certificates.py [-h] --user USER --password PASSWORD --rhost RHOST
                          [--debug]
                          {info,csrinfo,csr,install,delete} ...

A tool to manage certificates on a Redfish service

positional arguments:
  {info,csrinfo,csr,install,delete}
    info                Displays information about the certificates installed
                        on the service
    csrinfo             Displays information about options supported for
                        generating certificate signing requests
    csr                 Generates a certificate signing request
    install             Installs a certificate on the service
    delete              Deletes a certificate on the service

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


#### Info

```
usage: rf_certificates.py info [-h] [--details]

optional arguments:
  -h, --help           show this help message and exit
  --details, -details  Indicates if the full details of each certificate
                       should be shown
```

Example: `rf_certificates.py -u root -p root -r https://192.168.1.100 info`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the certificate service, find its certificate locations, and display the certificates.


#### Certificate Signing Request Info

```
usage: rf_certificates.py csrinfo [-h]

optional arguments:
  -h, --help  show this help message and exit
```

Example: `rf_certificates.py -u root -p root -r https://192.168.1.100 csrinfo`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the certificate service, find the `GenerateCSR` action, and display the information obtained from its action info.


#### Certificate Signing Request

```
usage: rf_certificates.py csr [-h] --certificatecollection
                              CERTIFICATECOLLECTION --commonname COMMONNAME
                              --organization ORGANIZATION --organizationalunit
                              ORGANIZATIONALUNIT --city CITY --state STATE
                              --country COUNTRY [--email EMAIL]
                              [--keyalg KEYALG] [--keylen KEYLEN]
                              [--keycurve KEYCURVE] [--out OUT]

required arguments:
  --certificatecollection CERTIFICATECOLLECTION, -col CERTIFICATECOLLECTION
                        The URI of the certificate collection where the signed
                        certificate will be installed
  --commonname COMMONNAME, -cn COMMONNAME
                        The common name of the component to secure
  --organization ORGANIZATION, -o ORGANIZATION
                        The name of the unit in the organization making the
                        request
  --organizationalunit ORGANIZATIONALUNIT, -ou ORGANIZATIONALUNIT
                        The name of the unit in the organization making the
                        request
  --city CITY, -l CITY  The city or locality of the organization making the
                        request
  --state STATE, -st STATE
                        The state, province, or region of the organization
                        making the request
  --country COUNTRY, -c COUNTRY
                        The two-letter country code of the organization making
                        the request

optional arguments:
  -h, --help            show this help message and exit
  --email EMAIL, -email EMAIL
                        The email address of the contact within the
                        organization making the request
  --keyalg KEYALG, -alg KEYALG
                        The type of key-pair for use with signing algorithms
  --keylen KEYLEN, -len KEYLEN
                        The length of the key, in bits, if the key pair
                        algorithm supports key size
  --keycurve KEYCURVE, -curve KEYCURVE
                        The curve ID to use with the key if the key pair
                        algorithm supports curves
  --out OUT, -out OUT   The file, with optional path, to save the certificate
                        signing request
```

Example: `rf_certificates.py -u root -p root -r https://192.168.1.100 csr -col /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates -cn "manager.contoso.org" -o "Contoso" -ou "Contoso HW Div" -l "Portland" -st "Oregon" -c "US"`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the certificate service, find the `GenerateCSR` action, invoke the `GenerateCSR` action with the provided arguments, and display the certificate signing request produced by the service.

#### Install

```
usage: rf_certificates.py install [-h] --destination DESTINATION --certificate
                                  CERTIFICATE [--key KEY]

required arguments:
  --destination DESTINATION, -dest DESTINATION
                        The installation URI of the certificate; either a
                        certificate collection to insert, or an existing
                        certificate to replace
  --certificate CERTIFICATE, -cert CERTIFICATE
                        The file, and optional path, of the certificate to
                        install

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -key KEY   The file, and optional path, of the private key for
                        the certificate to install
``` 

Example: `rf_licenses.py -u root -p root -r https://192.168.1.100 install --destination /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates/1 --cert /home/user/my_new_cert.pem`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then inspect the URI referenced by the *destination* argument.
If the *destination* is discovered to be a certificate collection, it will install the contents provided by the *certificate* and *key* arguments into the referenced collection.
Otherwise, it will locate the certificate service, find the `ReplaceCertificate` action, and invoke the action with the contents provided by the *certificate* and *key* arguments to replace the certificate referenced by the *destination* argument.

#### Delete

```
usage: rf_certificates.py delete [-h] --certificate CERTIFICATE

required arguments:
  --certificate CERTIFICATE, -cert CERTIFICATE
                        The URI of the certificate to delete

optional arguments:
  -h, --help            show this help message and exit
```

Example: `rf_certificates.py -u root -p root -r https://192.168.1.100 delete --certificate /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates/1`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then delete the certificate referenced by the *certificate* argument.


### Diagnostic Data

```
usage: rf_diagnostic_data.py [-h] --user USER --password PASSWORD --rhost
                             RHOST [--manager [MANAGER]] [--system [SYSTEM]]
                             [--chassis [CHASSIS]] [--log LOG]
                             [--type {Manager,PreOS,OS,OEM}]
                             [--oemtype OEMTYPE] [--directory DIRECTORY]

A tool to collect diagnostic data from a log service on a Redfish service

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
  --log LOG, -l LOG     The ID of the log service
  --type {Manager,PreOS,OS,OEM}, -type {Manager,PreOS,OS,OEM}
                        The type of diagnostic data to collect; defaults to
                        'Manager' if not specified
  --oemtype OEMTYPE, -oemtype OEMTYPE
                        The OEM-specific type of diagnostic data to collect;
                        this option should only be used if the requested type
                        is 'OEM'
  --directory DIRECTORY, -d DIRECTORY
                        The directory to save the diagnostic data; defaults to
                        the current directory if not specified
  --debug               Creates debug file showing HTTP traces and exceptions
```

Example: `rf_diagnostic_data.py -u root -p root -r https://192.168.1.100 -m BMC`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then attempt to locate the appropriate log service via the following logic:
* If the *manager* argument is provided, it will traverse the manager collection for the matching manager.
* If the *system* argument is provided, it will traverse the system collection for the matching system.
* If the *chassis* argument is provided, it will traverse the chassis collection for the matching chassis.
* If any of the above arguments are provided without a specified Id, but the collection contains exactly one member, then that member is used.
* If none of the above arguments are provided, then the tool will try to use a manager in the manager collection if there is only one member present.
* Within the member, the tool will find the matching log service based on the *log* argument.
    * If *log* is not specified, and there is exactly one log service in the member, then the tool will use that one log service.

Once the desired log service is found, the tool perform the `GetDiagnosticData` action and specify the type of diagnostic data to collect based on the *type* and *oemtype* arguments.  Once the action is complete, it will download the diagnostic data from the service and save it on the local system.


### Raw Request

```
usage: rf_raw_request.py [-h] --user USER --password PASSWORD --rhost RHOST
                         [--method {GET,HEAD,POST,PATCH,PUT,DELETE}] --request
                         REQUEST [--body BODY] [--verbose]

A tool perform a raw request to a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)
  --request REQUEST, -req REQUEST
                        The URI for the request

optional arguments:
  -h, --help            show this help message and exit
  --method {GET,HEAD,POST,PATCH,PUT,DELETE}, -m {GET,HEAD,POST,PATCH,PUT,DELETE}
                        The HTTP method to perform; performs GET if not
                        specified
  --body BODY, -b BODY  The body to provide with the request; can be a JSON
                        string for a JSON request, a filename to send binary
                        data, or an unstructured string
  --verbose, -v         Indicates if HTTP response codes and headers are
                        displayed
```

Example: `rf_raw_request.py -u root -p root -r https://192.168.1.100 -req /redfish/v1/Systems/1 -m PATCH -b '{"AssetTag": "New tag"}'`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then perform the requested method on the specified URI with an optional body, specified by the *method*, *request*, and *body* arguments.
It will then display the response of the operation from the service.


## Release Process

1. Go to the "Actions" page
2. Select the "Release and Publish" workflow
3. Click "Run workflow"
4. Fill out the form
5. Click "Run workflow"
