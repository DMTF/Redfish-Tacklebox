# Assembly (rf_assembly.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage assemblies on a Redfish service.

## Usage

```
usage: rf_assembly.py [-h] --user USER --password PASSWORD --rhost RHOST
                      --assembly ASSEMBLY [--index INDEX] [--debug]
                      {info,download,upload} ...

A tool to manage assemblies on a Redfish service

positional arguments:
  {info,download,upload}
    info                Displays information about the an assembly
    download            Downloads assembly data to a file
    upload              Uploads assembly data from a file

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)
  --assembly ASSEMBLY, -a ASSEMBLY
                        The URI of the target assembly

optional arguments:
  -h, --help            show this help message and exit
  --index INDEX, -i INDEX
                        The target assembly index
  --debug               Creates debug file showing HTTP traces and exceptions
```

### Info

Displays information about the an assembly.

```
usage: rf_assembly.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then get the assembly information from the URI specified by the *assembly* argument and displays its information.

Example:

```
$ rf_assembly.py -u root -p root -r https://192.168.1.100 -a /redfish/v1/Chassis/1U/PowerSubsystem/PowerSupplies/Bay1/Assembly info
 0     | Contoso Power Supply 
       | Model: 345TTT
       | PartNumber: 923943
       | SerialNumber: 345394834
       | Producer: Contoso Supply Co.
       | Vendor: Contoso
       | ProductionDate: 2017-04-01T14:55:33+03:00
```

### Download

Downloads assembly data to a file.

```
usage: rf_assembly.py download [-h] --file FILE

required arguments:
  --file FILE, -f FILE  The file, and optional path, to save the assembly data

optional arguments:
  -h, --help            show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then get the assembly information from the URI specified by the *assembly* argument and download the binary data contents to the file specified by the *file* argument.

```
$ rf_assembly.py -u root -p root -r https://192.168.1.100 -a /redfish/v1/Chassis/1U/PowerSubsystem/PowerSupplies/Bay1/Assembly download -f data.bin
Saving data to 'data.bin'...
```

### Upload

Uploads assembly data from a file.

```
usage: rf_assembly.py upload [-h] --file FILE

required arguments:
  --file FILE, -f FILE  The file, and optional path, containing the assembly
                        data to upload

optional arguments:
  -h, --help            show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then get the assembly information from the URI specified by the *assembly* argument and upload the contents of the file specified by the *file* argument to the binary data.

```
$ rf_assembly.py -u root -p root -r https://192.168.1.100 -a /redfish/v1/Chassis/1U/PowerSubsystem/PowerSupplies/Bay1/Assembly upload -f data.bin
Writing data from 'data.bin'...
```
