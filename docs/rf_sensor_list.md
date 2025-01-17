# Sensor List (rf_sensor_list.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool to walk a Redfish service and list sensor info.

## Usage

```
usage: rf_sensor_list.py [-h] --user USER --password PASSWORD --rhost RHOST
                         [--id] [--name] [--debug]

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

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It then traverses the chassis collection for the service, and reads their respective power and thermal resources.
Using the information from those resources, it will build a sensor table and print the information collected.

Example:

```
$ rf_sensor_list.py -u root -p root -r https://192.168.1.100
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading      | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext                 
  State                     | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Power Supply Bay 1 State  | Enabled      | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Power Supply Bay 2 State  | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 State           | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 StoredEnergyWat | 19.41 W.h    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 ChargePercent   | 100 %        | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 0  | 3.44 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 1  | 3.45 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 2  | 3.43 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 3  | 3.43 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 4  | 3.45 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 5  | 3.44 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 6  | 3.43 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Battery 1 CellVoltages 7  | 3.44 V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Power Supply Redundancy 0 | UnavailableOffline | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Fan Bay 1 State           | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Fan Bay 2 State           | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Fan for CPU 1 State       | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Fan for CPU 2 State       | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Fan Redundancy 0          | Enabled      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Fan Redundancy 1          | Disabled     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A                             
  Ambient Temperature       | 22.50 Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Room                            
  CPU #1 Fan Speed          | 80 %         | OK       | N/A      | 0        | 5        | N/A      | N/A      | N/A      | CPU                             
  CPU #2 Fan Speed          | 60 %         | OK       | N/A      | 0        | 5        | N/A      | N/A      | N/A      | CPU                             
  CPU #1 Temperature        | 37 Cel       | OK       | N/A      | N/A      | N/A      | 42       | 45       | 50       | CPU                             
  DIMM #1 Temperature       | 44 Cel       | OK       | N/A      | N/A      | N/A      | 55       | 65       | 75       | Memory                          
  DIMM #2 Temperature       | 43 Cel       | OK       | N/A      | N/A      | N/A      | 55       | 65       | 75       | Memory                          
  DIMM #3 Temperature       | 45 Cel       | OK       | N/A      | N/A      | N/A      | 55       | 65       | 75       | Memory                          
  Fan Bay #1 Exhaust Temper | 40.50 Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Exhaust                         
  Chassis Fan #1            | 45 %         | OK       | N/A      | 0        | 5        | N/A      | N/A      | N/A      | Chassis                         
  Chassis Fan #2            | 45 %         | OK       | N/A      | 0        | 5        | N/A      | N/A      | N/A      | Chassis                         
  Front Panel Intake Temper | 24.80 Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake                          
  Power Supply #1 Energy    | 7855 kW.h    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #1 Frequency | 60.10 Hz     | OK       | N/A      | 58.75    | 59.5     | 60.2     | 60.37    | N/A      | PowerSupply                     
  Power Supply #1 Input Cur | 8.92 A       | OK       | N/A      | N/A      | N/A      | 9        | 10       | N/A      | PowerSupply                     
  Power Supply #1 Input Pow | 374 W        | OK       | N/A      | N/A      | N/A      | 510      | 525      | N/A      | PowerSupply                     
  Power Supply #1 Input Vol | 119.27 V     | OK       | N/A      | 115      | 118      | 122      | 125      | N/A      | PowerSupply                     
  Power Supply #1 12V Outpu | 12.08 V      | OK       | N/A      | 11.5     | 11.85    | 12.35    | 12.5     | N/A      | PowerSupply                     
  Power Supply #1 12V Outpu | 2.79 A       | OK       | N/A      | N/A      | N/A      | 6        | 7        | N/A      | Chassis                         
  Power Supply #1 3V Output | 3.32 V       | OK       | N/A      | 3.1      | 3.25     | 3.35     | 3.5      | N/A      | PowerSupply                     
  Power Supply #1 3V Output | 8.92 A       | OK       | N/A      | N/A      | N/A      | 20       | 25       | N/A      | PowerSupply                     
  Power Supply #1 5V Output | 5.04 V       | OK       | N/A      | 4.5      | 4.9      | 5.35     | 5.5      | N/A      | PowerSupply                     
  Power Supply #1 5V Output | 3.41 A       | OK       | N/A      | N/A      | N/A      | 5        | 8        | N/A      | PowerSupply                     
  Power Supply #2 Energy    | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 Frequency | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 Input Cur | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 Input Pow | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 Input Vol | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 12V Outpu | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 12V Outpu | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 3V Output | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 3V Output | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 5V Output | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Power Supply #2 5V Output | Absent       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | PowerSupply                     
  Total Energy              | 325675 kW.h  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Chassis                         
  Power reading for the Cha | 374 W        | OK       | N/A      | N/A      | N/A      | 580      | 600      | N/A      | Chassis                         
  Battery #1 Temperature    | 33 Cel       | OK       | N/A      | N/A      | N/A      | 50       | 60       | N/A      | Battery                         
  Battery #1 Input Voltage  | 12.22 V      | OK       | N/A      | N/A      | N/A      | 13       | 14       | N/A      | Battery                         
  Battery #1 Input Current  | 0 A          | OK       | N/A      | N/A      | N/A      | 55       | 60       | N/A      | Battery                         
  Battery #1 Output Voltage | 12.22 V      | OK       | N/A      | N/A      | N/A      | 13       | 14       | N/A      | Battery                         
  Battery #1 Output Current | 0 A          | OK       | N/A      | N/A      | N/A      | 8        | 10       | N/A      | Battery                         
  Battery #1 State of Healt | 91 %         | OK       | N/A      | 30       | N/A      | N/A      | N/A      | N/A      | Battery                         

```
