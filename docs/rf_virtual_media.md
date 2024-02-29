# Virtual Media (rf_virtual_media.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage virtual media of a system.

## Usage

```
usage: rf_virtual_media.py [-h] --user USER --password PASSWORD --rhost RHOST
                           [--system SYSTEM] [--debug]
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

### Info

Displays information about the virtual media for a system.

```
usage: rf_virtual_media.py info [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the system specified by the *system* argument, find its virtual media collection, and display the virtual media instances.

Example:

```
$ rf_virtual_media.py -u root -p root -r https://192.168.1.100 info

  Floppy1              | ImageName: Sardine2.1.43.35.6a
                       | Image: https://www.dmtf.org/freeImages/Sardine.img
                       | MediaTypes: Floppy, USBStick
                       | ConnectedVia: URI
                       | Inserted: True
                       | WriteProtected: False

  CD1                  | ImageName: mymedia-read-only
                       | Image: redfish.dmtf.org/freeImages/freeOS.1.1.iso
                       | MediaTypes: CD, DVD
                       | ConnectedVia: Applet
                       | Inserted: True
                       | WriteProtected: False

```

### Insert

Inserts virtual media for a system.

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

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the system specified by the *system* argument, find its virtual media collection.
It will then iterate through the virtual media collection, and insert the virtual media specified by the *image* argument in an appropriate slot.

Example:

```
$ rf_virtual_media.py -u root -p root -r https://192.168.1.100 insert -image http://somefileserver/my_media.iso
Inserting 'http://somefileserver/my_media.iso'
```

### Eject

Ejects virtual media from a system.

```
usage: rf_virtual_media.py eject [-h] --id ID

required arguments:
  --id ID, -i ID  The identifier of the virtual media instance to eject

optional arguments:
  -h, --help      show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the system specified by the *system* argument, find its virtual media collection.
It will then locate the virtual media instance with matching `Id` property with the *id* argument, and then eject the media.

Example:

```
$ rf_virtual_media.py -u root -p root -r https://192.168.1.100 eject --id CD1
Ejecting 'CD1'
```
