# Power Equipment (rf_power_equipment.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage power equipment.

## Usage

```
usage: rf_power_equipment.py [-h] --user USER --password PASSWORD --rhost
                             RHOST [--debug]
                             {list,status,outlets,outletinfo,mainsinfo,branchinfo}
                             ...

A tool to manage power equipment

positional arguments:
  {list,status,outlets,outletinfo,mainsinfo,branchinfo}
    list                Displays a list of the available power equipment
    status              Displays the status of an instance of power equipment
    outlets             Displays the outlet summary of an instance of power
                        equipment
    outletinfo          Displays the status of an outlet for an instance of
                        power equipment
    mainsinfo           Displays the status of a mains circuit for an instance
                        of power equipment
    branchinfo          Displays the status of a branch circuit for an
                        instance of power equipment

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

### List

Displays a list of the available power equipment.

```
usage: rf_power_equipment.py list [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the power equipment monitored by the service and construct a table of the available equipment categorized by the equipment type.

Example:

```
$ rf_power_equipment.py -u root -p root -r https://192.168.1.100 list
FloorPDUs
  Id               | Model            | Serial Number    | State        | Health  
  1                | GLH9000          | 0458329          | Enabled      | OK      

RackPDUs
  Id               | Model            | Serial Number    | State        | Health  
  1                | ZAP4000          | 29347ZT536       | Enabled      | OK      

TransferSwitches
  Id               | Model            | Serial Number    | State        | Health  
  1                | ZAP4000          | 29347ZT536       | Enabled      | OK      

```

### Status

Displays the status of an instance of power equipment.

```
usage: rf_power_equipment.py status [-h] --type
                                    {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                                    [--equipment EQUIPMENT]

required arguments:
  --type {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}, -t {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                        The type of power equipment to get

optional arguments:
  -h, --help  show this help message and exit
  --equipment EQUIPMENT, -pe EQUIPMENT
                        The identifier of the power equipment to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument, and displays the equipment instance with summary information about any mains and branch circuits found.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.

Example:

```
$ rf_power_equipment.py -u root -p root -r https://192.168.1.100 status -t RackPDU -pe 1
RackPDU 1 Info

  Status: State: Enabled, Health: OK
  EquipmentType: RackPDU
  Model: ZAP4000
  Manufacturer: Contoso
  PartNumber: AA-23
  SerialNumber: 29347ZT536
  Version: 1.03b
  FirmwareVersion: 4.3.0
  ProductionDate: 2017-01-11T08:00:00Z
  AssetTag: PDX-92381
  Power: 6438 W
  Energy: 56438 kWh
  Temperature: 31 C

  Mains Id         | Nominal Voltage    | Phase Wiring         | State        | Voltage (V)  | Current (A)  | Power (W)   
  AC1              | 200 V to 240 V AC  | 3 Phase, 5 Wire      | ---          | Polyphase    | Polyphase    | ---         

  Branch Id        | Nominal Voltage    | Phase Wiring         | State        | Voltage (V)  | Current (A)  | Power (W)   
  A                | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 937.4       
  B                | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 977.8       
  C                | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 816.5       

```

### Outlets

Displays the outlet summary of an instance of power equipment.

```
usage: rf_power_equipment.py outlets [-h] --type
                                     {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                                     [--equipment EQUIPMENT]

required arguments:
  --type {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}, -t {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                        The type of power equipment to get

optional arguments:
  -h, --help  show this help message and exit
  --equipment EQUIPMENT, -pe EQUIPMENT
                        The identifier of the power equipment to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument, and displays the outlet summary for the equipment.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.

Example:

```
$ rf_power_equipment.py -u root -p root -r https://192.168.1.100 outlets -t RackPDU -pe 1
RackPDU 1 Outlets

  Outlet Id        | Nominal Voltage    | Phase Wiring         | State        | Voltage (V)  | Current (A)  | Power (W)   
  A1               | 120 V AC           | 1 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 197.4       
  A2               | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 384.5       
  A3               | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 349.9       
  A4               | 120 V AC           | 1 Phase, 3 Wire      | Enabled      | ---          | ---          | ---         
  A5               | 120 V AC           | 1 Phase, 3 Wire      | ---          | ---          | ---          | ---         
  B1               | 120 V AC           | 1 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 228.3       
  B2               | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 321.6       
  B3               | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 426.5       
  C1               | 120 V AC           | 1 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 56.8        
  C2               | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 394.1       
  C3               | 200 V to 240 V AC  | 2 Phase, 3 Wire      | Enabled      | Polyphase    | Polyphase    | 355.4       

```

### Outlet Info

Displays the status of an outlet for an instance of power equipment.

```
rf_power_equipment.py outletinfo --help
usage: rf_power_equipment.py outletinfo [-h] --type
                                        {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                                        [--equipment EQUIPMENT]
                                        [--outlet OUTLET]

required arguments:
  --type {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}, -t {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                        The type of power equipment to get
                        
optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -pe EQUIPMENT
                        The identifier of the power equipment to get
  --outlet OUTLET, -o OUTLET
                        The identifier of the outlet to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the outlet specified by the *outlet* argument, and displays the outlet info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *outlet* is not specified, and if the equipment has exactly one outlet, it will perform the operation on the one outlet.

Example:

```
$ rf_power_equipment.py -u root -p root -r https://192.168.1.100 outletinfo -t RackPDU -pe 1 -o A1
Outlet A1 Info

  Status: State: Enabled, Health: OK
  PhaseWiringType: 1 Phase, 3 Wire
  VoltageType: AC
  OutletType: NEMA 5-20R (120V; 20A)
  NominalVoltage: 120 V AC
  RatedCurrentAmps: 20
  PowerState: On
  Voltage: 117.5 V
    L1-N :  117.50 V
  Current: 1.68 A
    L1   :    1.68 A
  Power: 197.4 W
  Energy: 36166 kWh
  Frequency: 60.1 Hz

```

### Mains Info

Displays the status of a mains circuit for an instance of power equipment.

```
usage: rf_power_equipment.py mainsinfo [-h] --type
                                       {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                                       [--equipment EQUIPMENT] [--mains MAINS]

required arguments:
  --type {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}, -t {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                        The type of power equipment to get
                        
optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -pe EQUIPMENT
                        The identifier of the power equipment to get
  --mains MAINS, -m MAINS
                        The identifier of the mains circuit to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the mains circuit specified by the *mains* argument, and displays the mains circuit info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *mains* is not specified, and if the equipment has exactly one mains circuit, it will perform the operation on the one mains circuit.

Example:

```
$ rf_power_equipment.py -u root -p root -r https://192.168.1.100 mainsinfo -t RackPDU -pe 1 -m AC1
Mains AC1 Info

  Status: State: N/A, Health: OK
  CircuitType: Mains
  PhaseWiringType: 3 Phase, 5 Wire
  NominalVoltage: 200 V to 240 V AC
  RatedCurrentAmps: 40
  BreakerState: Normal
  Voltage: 
    L1-L2:  202.80 V
    L1-N :  117.80 V
    L2-L3:  203.80 V
    L2-N :  116.60 V
    L3-L1:  205.30 V
    L3-N :  118.50 V
  Current: 
    L1   :    8.02 A
    L2   :    8.66 A
    L3   :    6.91 A
    N    :    2.74 A
  Power: 
    L1-L2:  738.90 W
    L1-N :  198.40 W
    L2-L3:  748.30 W
    L2-N :  231.50 W
    L3-L1:  759.60 W
    L3-N :   58.10 W
  Frequency: 60.1 Hz

```

### Branch Info

Displays the status of a branch circuit for an instance of power equipment.

```
usage: rf_power_equipment.py branchinfo [-h] --type
                                        {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                                        [--equipment EQUIPMENT]
                                        [--branch BRANCH]

required arguments:
  --type {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}, -t {FloorPDU,RackPDU,Switchgear,TransferSwitch,PowerShelf,ElectricalBus}
                        The type of power equipment to get
                        
optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -pe EQUIPMENT
                        The identifier of the power equipment to get
  --branch BRANCH, -b BRANCH
                        The identifier of the branch circuit to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the branch circuit specified by the *branch* argument, and displays the branch circuit info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *branch* is not specified, and if the equipment has exactly one branch circuit, it will perform the operation on the one branch circuit.

Example:

```
$ rf_power_equipment.py -u root -p root -r https://192.168.1.100 branchinfo -t RackPDU -pe 1 -b C
Branch C Info

  Status: State: Enabled, Health: OK
  CircuitType: Branch
  PhaseWiringType: 2 Phase, 3 Wire
  NominalVoltage: 200 V to 240 V AC
  RatedCurrentAmps: 16
  BreakerState: Normal
  Voltage: 
    L3-L1:  205.10 V
    L3-N :  118.40 V
  Current: 4.13 A
    L3   :    4.13 A
  Power: 816.5 W
    L1-N :  816.50 W
  Energy: 121666 kWh
  Frequency: 60.1 Hz

```
