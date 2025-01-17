# Manager Configuration (rf_manager_config.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to manage managers in a service.

## Usage

```
usage: rf_manager_config.py [-h] --user USER --password PASSWORD --rhost RHOST
                            [--manager MANAGER] [--debug]
                            {info,reset,getnet,setnet,resettodefaults,settime,getprotocol,setprotocol}
                            ...

A tool to manage managers in a service

positional arguments:
  {info,reset,getnet,setnet,resettodefaults,settime,getprotocol,setprotocol}
    info                Displays information about a manager
    reset               Resets a manager
    getnet              Displays information about an Ethernet interface
    setnet              Configures an Ethernet interface
    resettodefaults     Resets a manager to default settings
    settime             Sets the date-time on a manager
    getprotocol         Displays network protocol information about a manager
    setprotocol         Configures network protocol settings on a manager

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

### Info

Displays information about a manager.

```
usage: rf_manager_config.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, and displays the manager instance.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 info
Manager BMC Info
  Status: State: Enabled, Health: OK
  ManagerType: BMC
  PowerState: On
  FirmwareVersion: 1.45.455b66-rev4
  DateTime: 2015-03-13T04:14:33+06:00
  DateTimeLocalOffset: +06:00
  UUID: 58893887-8974-2487-2389-841168418919
  ServiceEntryPointUUID: 92384634-2938-2342-8820-489239905423
  Model: Joo Janta 200

```

### Reset

Resets a manager.

```
usage: rf_manager_config.py reset [-h]
                                  [--type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}]
                                  [--info]

optional arguments:
  -h, --help            show this help message and exit
  --type {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}, -t {On,ForceOff,GracefulShutdown,GracefulRestart,ForceRestart,Nmi,ForceOn,PushPowerButton,PowerCycle,Suspend,Pause,Resume}
                        The type of power/reset operation to perform
  --info, -info         Indicates if reset information should be reported
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the manager collection for the service to find the matching manager specified by the *manager* argument.
It will perform the `Reset` action with the specified reset type from the *type* argument.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *type* is not specified, it will attempt a `GracefulRestart`.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 reset -t GracefulRestart
Resetting the manager...
```

### Get Network Interface

Displays information about an Ethernet interface.

```
usage: rf_manager_config.py getnet [-h] [--id ID]

optional arguments:
  -h, --help      show this help message and exit
  --id ID, -i ID  The identifier of the Ethernet interface to display
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, locate the Ethernet interface specified by the *id* argument, and displays the interface instance.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *id* is not specified, and if the manager has exactly one Ethernet interface, it will perform the operation on the one interface.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 getnet -i NIC2
Ethernet Interface NIC2 Info
  Status: State: Enabled, Health: OK
  InterfaceEnabled: True
  LinkStatus: LinkUp
  MACAddress: 23:11:8A:33:CF:EA
  PermanentMACAddress: 23:11:8A:33:CF:EA
  SpeedMbps: 100
  AutoNeg: True
  FullDuplex: True
  MTUSize: 1500
  HostName: web483-bmc
  FQDN: web483-bmc.dmtf.org
  NameServers: names.dmtf.org

  VLAN Info
    Enabled: True
    ID: 101
    Priority: N/A

  IPv4 Info
    Assigned Addresses
      192.168.0.10: 255.255.252.0, 192.168.0.1, DHCP

  IPv6 Info
    Assigned Addresses
      fe80::1ec1:deff:fe6f:1e24/64: SLAAC, Preferred
    Static Addresses
      fe80::1ec1:deff:fe6f:1e24/16
    Default Gateway: fe80::1ec1:deff:fe6f:1e24
    Address Policy Table
      Prefix: ::1/128, Prec: 50, Label: 0

```

### Set Network Interface

Configures an Ethernet interface.

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

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, locate the Ethernet interface specified by the *id* argument, and apply the requested settings to the interface.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *id* is not specified, and if the manager has exactly one Ethernet interface, it will perform the operation on the one interface.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 setnet -i NIC2 -ipv4address 192.168.1.101 -ipv4gateway 192.168.1.1
```

### Reset to Defaults

Resets a manager to default settings.

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

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the manager collection for the service to find the matching manager specified by the *manager* argument.
It will perform the `ResetToDefaults` action with the specified reset type from the *type* argument.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.
* If *type* is not specified, it will attempt to perform the action with `PreserveNetworkAndUsers`.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 resettodefaults -t ResetAll
Resetting the manager to defaults...
```

### Set Time

Sets the date-time on a manager.

```
usage: rf_manager_config.py settime [-h] [--datetime DATETIME]
                                    [--offset OFFSET]

optional arguments:
  -h, --help            show this help message and exit
  --datetime DATETIME, -dt DATETIME
                        The date-time value to set
  --offset OFFSET, -o OFFSET
                        The date-time offset value to set
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the manager specified by the *manager* argument, and applies the *datetime* and *offset* values to the manager instance.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.

Example; set a date-time:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 settime -dt 2023-07-27T12:00:00-05:00
```

Example; set a date-time offset:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 settime -o=-05:00
```

### Get Network Protocol Information

Displays network protocol information about a manager.

```
usage: rf_manager_config.py getprotocol [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the manager collection for the service to find the matching manager specified by the *manager* argument and displays its network protocol information.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 getprotocol
Manager Network Protocol Info

  Protocol         | Enabled  | Port   | Other Settings
  HTTP             | True     | 80     | 
  HTTPS            | True     | 443    | 
  SSDP             | True     | 1900   | NOTIFY IPv6 Scope: Site, NOTIFY TTL: 5, NOTIFY ALIVE Interval: 600
  SSH              | True     | 22     | 
  Telnet           | True     | 23     | 
  KVMIP            | True     | 5288   | 
  VirtualMedia     | True     | 17988  | 
  IPMI             | True     | 623    | 
  SNMP             | True     | 161    | 
```

### Set Network Protocol Information

Configures network protocol settings on a manager.

```
usage: rf_manager_config.py setprotocol [-h] --protocol PROTOCOL [--enable]
                                        [--disable] [--port PORT]

required arguments:
  --protocol PROTOCOL, -prot PROTOCOL
                        The protocol to set

optional arguments:
  -h, --help            show this help message and exit
  --enable, -en         Enable the selected protocol
  --disable, -dis       Disable the selected protocol
  --port PORT, -port PORT
                        The port number to assign the protocol
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the manager collection for the service to find the matching manager specified by the *manager* argument and apply the configuration specified by the *enable*, *disable*, and *port* arguments to the protocol specified by the *protocol* argument.

* If *manager* is not specified, and if the service has exactly one manager, it will perform the operation on the one manager.

Example:

```
$ rf_manager_config.py -u root -p root -r https://192.168.1.100 setprotocol -prot IPMI -dis
Configuring IPMI...
```
