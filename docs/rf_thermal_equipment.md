# Thermal Equipment (rf_thermal_equipment.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage thermal equipment.

## Usage

```
usage: rf_thermal_equipment.py [-h] --user USER --password PASSWORD --rhost
                               RHOST [--debug]
                               {list,status,primaryinfo,secondaryinfo,pumpinfo,filterinfo,reservoirinfo,leakdetectors}
                               ...

A tool to manage thermal equipment

positional arguments:
  {list,status,primaryinfo,secondaryinfo,pumpinfo,filterinfo,reservoirinfo,leakdetectors}
    list                Displays a list of the available thermal equipment
    status              Displays the status of an instance of thermal
                        equipment
    primaryinfo         Displays the status of a primary coolant connector for
                        an instance of thermal equipment
    secondaryinfo       Displays the status of a secondary coolant connector
                        for an instance of thermal equipment
    pumpinfo            Displays the status of a pump for an instance of
                        thermal equipment
    filterinfo          Displays the status of a filter for an instance of
                        thermal equipment
    reservoirinfo       Displays the status of a reservoir for an instance of
                        thermal equipment
    leakdetectors       Displays the leak detector summary of an instance of
                        thermal equipment

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

Displays a list of the available thermal equipment.

```
usage: rf_thermal_equipment.py list [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the thermal equipment monitored by the service and construct a table of the available equipment categorized by the equipment type.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 list
CDUs
  Id               | Model            | Serial Number    | State        | Health  
  1                | BRRR4000         | 29347ZT536       | Enabled      | OK      

```

### Status

Displays the status of an instance of thermal equipment.

```
usage: rf_thermal_equipment.py status [-h] --type
                                      {CDU,HeatExchanger,ImmersionUnit}
                                      [--equipment EQUIPMENT]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument, and displays the equipment instance with summary information about any sub components and leak detectors found.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 status -t CDU -te 1
CDU 1 Info

  Status: State: Enabled, Health: OK
  EquipmentType: CDU
  Model: BRRR4000
  Manufacturer: Contoso
  PartNumber: ICE-9
  SerialNumber: 29347ZT536
  Version: 1.03b
  FirmwareVersion: 3.2.0
  ProductionDate: 2020-12-24T08:00:00Z
  AssetTag: PDX5-92381
  Coolant: Water, 20 % Glycol, Specific Heat: 3.974 kJ/kg/K, Density: 1030 kg/m3
  Temperature: 24 C
  Humidity: 26 %
  Detectors in the CDU: OK, Humidity: 26 %

  Primary Id       | Flow (L/min) | Supply T (C) | Supply P (kPa) | Return T (C) | Return P (kPa)
  1                | 42           | 30           | 827            | 40           | 965           

  Secondary Id     | Flow (L/min) | Supply T (C) | Supply P (kPa) | Return T (C) | Return P (kPa)
  1                | 42           | 30           | 103            | 48           | 137           

  Pump Id          | Type         | State        | Health       | Speed (%)   
  1                | Liquid       | Enabled      | OK           | 38.5        

  Filter Id        | State        | Health       | Serviced Date             | Service Hours
  1                | Enabled      | OK           | 2020-12-24T08:00:00Z      | 5791        

  Reservoir Id     | Type         | State        | Health       | Fluid Status        
  1                | Inline       | Enabled      | OK           | OK                  

```

### Primary Info

Displays the status of a primary coolant connector for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py primaryinfo [-h] --type
                                           {CDU,HeatExchanger,ImmersionUnit}
                                           [--equipment EQUIPMENT]
                                           [--primary PRIMARY]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
  --primary PRIMARY, -pr PRIMARY
                        The identifier of the primary coolant connector to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the primary coolant connector specified by the *primary* argument, and displays the primary coolant connector info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *primary* is not specified, and if the equipment has exactly one primary coolant connector, it will perform the operation on the one primary coolant connector.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 primaryinfo -t CDU -te 1 -pr 1
Primary Connector 1 Info

  Status: State: Enabled, Health: OK
  CoolantConnectorType: Pair
  Coolant: Water, 0 % Generic cooling water biocide
  RatedFlowLitersPerMinute: 50
  Flow: 42 L/min
  HeatRemoved: 25.48 kW
  SupplyTemperature: 30 C
  ReturnTemperature: 40 C
  DeltaTemperature: 10 C
  SupplyPressure: 827 kPa
  ReturnPressure: 965 kPa
  DeltaPressure: 138 kPa
  Temperature: Supply 30 C, Return 40 C, Delta 10 C
  Pressure: Supply 827 kPa, Return 965 kPa, Delta 138 kPa

```

### Secondary Info

Displays the status of a secondary coolant connector for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py secondaryinfo [-h] --type
                                             {CDU,HeatExchanger,ImmersionUnit}
                                             [--equipment EQUIPMENT]
                                             [--secondary SECONDARY]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
  --secondary SECONDARY, -sec SECONDARY
                        The identifier of the secondary coolant connector to
                        get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the secondary coolant connector specified by the *secondary* argument, and displays the secondary coolant connector info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *secondary* is not specified, and if the equipment has exactly one secondary coolant connector, it will perform the operation on the one secondary coolant connector.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 secondaryinfo -t CDU -te 1 -sec 1
Secondary Connector 1 Info

  Status: State: Enabled, Health: OK
  CoolantConnectorType: Pair
  Coolant: Water, 0 % Generic cooling water biocide
  RatedFlowLitersPerMinute: 50
  Flow: 42 L/min
  HeatRemoved: 25.31 kW
  SupplyTemperature: 30 C
  ReturnTemperature: 48 C
  DeltaTemperature: 18 C
  SupplyPressure: 103 kPa
  ReturnPressure: 137 kPa
  DeltaPressure: 34 kPa
  Temperature: Supply 30 C, Return 48 C, Delta 18 C
  Pressure: Supply 103 kPa, Return 137 kPa, Delta 34 kPa

```

### Pump Info

Displays the status of a pump for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py pumpinfo [-h] --type
                                        {CDU,HeatExchanger,ImmersionUnit}
                                        [--equipment EQUIPMENT] [--pump PUMP]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
  --pump PUMP, -pu PUMP
                        The identifier of the pump to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the pump specified by the *pump* argument, and displays the pump info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *pump* is not specified, and if the equipment has exactly one pump, it will perform the operation on the one pump.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 pumpinfo -t CDU -te 1 -pu 1
Service responded with invalid JSON at URI /redfish/v1/SessionService/Sessions

Pump 1 Info

  Status: State: Enabled, Health: OK
  PumpType: Liquid
  ServiceHours: 3571
  PumpSpeed: 38.5 %

```

### Filter Info

Displays the status of a filter for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py filterinfo [-h] --type
                                          {CDU,HeatExchanger,ImmersionUnit}
                                          [--equipment EQUIPMENT]
                                          [--filter FILTER]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
  --filter FILTER, -fil FILTER
                        The identifier of the filter to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the filter specified by the *filter* argument, and displays the filter info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *filter* is not specified, and if the equipment has exactly one filter, it will perform the operation on the one filter.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 filterinfo -t CDU -te 1 -fil 1
Filter 1 Info

  Status: State: Enabled, Health: OK
  ServicedDate: 2020-12-24T08:00:00Z
  ServiceHours: 5791
  RatedServiceHours: 10000
  Replaceable: True
  HotPluggable: False

```

### Reservoir Info

Displays the status of a reservoir for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py reservoirinfo [-h] --type
                                             {CDU,HeatExchanger,ImmersionUnit}
                                             [--equipment EQUIPMENT]
                                             [--reservoir RESERVOIR]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
  --reservoir RESERVOIR, -res RESERVOIR
                        The identifier of the reservoir to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the reservoir specified by the *reservoir* argument, and displays the reservoir info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *reservoir* is not specified, and if the equipment has exactly one reservoir, it will perform the operation on the one reservoir.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 reservoirinfo -t CDU -te 1 -res 1
Reservoir 1 Info

  Status: State: Enabled, Health: OK
  FluidLevelStatus: OK
  ReservoirType: Inline
  CapacityLiters: 1

```

### Filter Info

Displays the status of a filter for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py filterinfo [-h] --type
                                          {CDU,HeatExchanger,ImmersionUnit}
                                          [--equipment EQUIPMENT]
                                          [--filter FILTER]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
  --filter FILTER, -fil FILTER
                        The identifier of the filter to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the filter specified by the *filter* argument, and displays the filter info.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.
* If *filter* is not specified, and if the equipment has exactly one filter, it will perform the operation on the one filter.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 filterinfo -t CDU -te 1 -fil 1
Filter 1 Info

  Status: State: Enabled, Health: OK
  ServicedDate: 2020-12-24T08:00:00Z
  ServiceHours: 5791
  RatedServiceHours: 10000
  Replaceable: True
  HotPluggable: False

```

### Leak Detectors

Displays a table of the leak detectors for an instance of thermal equipment.

```
usage: rf_thermal_equipment.py leakdetectors [-h] --type
                                             {CDU,HeatExchanger,ImmersionUnit}
                                             [--equipment EQUIPMENT]

required arguments:
  --type {CDU,HeatExchanger,ImmersionUnit}, -t {CDU,HeatExchanger,ImmersionUnit}
                        The type of thermal equipment to get

optional arguments:
  -h, --help            show this help message and exit
  --equipment EQUIPMENT, -te EQUIPMENT
                        The identifier of the thermal equipment to get
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the equipment specified by the *equipment* argument for the type specified by the *type* argument.
It will then locate the leak detection information and displays it as a set of tables based on their groupings.

* If *equipment* is not specified, and if the service has exactly one equipment of the desired type, it will perform the operation on the one equipment.

Example:

```
$ rf_thermal_equipment.py -u root -p root -r https://192.168.1.100 leakdetectors -t CDU -te 1
CDU 1 Leak Detection

Detectors in the CDU: OK, Humidity: 26 %
  Detector Id      | Name                           | State       
  Moisture         | Moisture Leak Detector         | OK          
  Overflow         | Fluid Level Overflow           | OK          

```
