#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Sensors Module

File : sensors.py

Brief : This file contains the definitions and functionalities for scanning a
        Redfish service's Power and Thermal properties for sensor readings
"""

def get_sensors( context ):
    """
    Walks a Redfish service for Power and Thermal resources to return sensors

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all Power and Thermal readings
    """

    sensor_list = []

    # Get the Service Root to find the Chassis Collection
    service_root = context.get( "/redfish/v1/" )
    if "Chassis" not in service_root.dict:
        # No Chassis Collection
        return sensor_list

    # Get the Chassis Collection and iterate through its collection
    chassis_col = context.get( service_root.dict["Chassis"]["@odata.id"] )
    for chassis_member in chassis_col.dict["Members"]:
        chassis = context.get( chassis_member["@odata.id"] )

        # Get the Chassis status
        chassis_instance = {
            "ChassisName": chassis.dict["Id"],
            "Readings": []
        }
        sensor_list.append( chassis_instance )
        get_discrete_status( "State", chassis.dict, chassis_instance["Readings"] )

        # If there's a Power resource, read it
        if "Power" in chassis.dict:
            power = context.get( chassis.dict["Power"]["@odata.id"] )

            # Add information for each power supply reported
            if "PowerSupplies" in power.dict:
                for power_supply in power.dict["PowerSupplies"]:
                    power_supply_name = "Power Supply " + power_supply["MemberId"]
                    if "Name" in power_supply:
                        power_supply_name = power_supply["Name"]
                    get_discrete_status( power_supply_name + " State", power_supply, chassis_instance["Readings"] )
                    get_analog_status_small( power_supply_name, "ReadingVolts", "V", power_supply, chassis_instance["Readings"] )
                    get_analog_status_small( power_supply_name, "LineInputVoltage", "V", power_supply, chassis_instance["Readings"] )
                    get_analog_status_small( power_supply_name, "PowerCapacityWatts", "W", power_supply, chassis_instance["Readings"] )
                    get_analog_status_small( power_supply_name, "LastPowerOutputWatts", "W", power_supply, chassis_instance["Readings"] )

            # Add information for each of the voltages reported
            if "Voltages" in power.dict:
                for voltage in power.dict["Voltages"]:
                    voltage_name = "Voltage " + voltage["MemberId"]
                    if "Name" in voltage:
                        voltage_name = voltage["Name"]
                    get_analog_status_full( voltage_name, voltage, chassis_instance["Readings"] )

            # Add information for each of the redundancy groups reported
            if "Redundancy" in power.dict:
                for redundancy in power.dict["Redundancy"]:
                    get_discrete_status( redundancy["Name"], redundancy, chassis_instance["Readings"] )

        # If there's a Thermal resource, read it
        if "Thermal" in chassis.dict:
            thermal = context.get( chassis.dict["Thermal"]["@odata.id"] )

            # Add information for each of the temperatures reported
            if "Temperatures" in thermal.dict:
                for temperature in thermal.dict["Temperatures"]:
                    temperature_name = "Temperature " + temperature["MemberId"]
                    if "Name" in temperature:
                        temperature_name = temperature["Name"]
                    get_analog_status_full( temperature_name, temperature, chassis_instance["Readings"] )

            # Add information for each of the fans reported
            if "Fans" in thermal.dict:
                for fan in thermal.dict["Fans"]:
                    fan_name = "Fan " + fan["MemberId"]
                    if "Name" in fan:
                        fan_name = fan["Name"]
                    get_analog_status_full( fan_name, fan, chassis_instance["Readings"] )

            # Add information for each of the redundancy groups reported
            if "Redundancy" in thermal.dict:
                for redundancy in thermal.dict["Redundancy"]:
                    get_discrete_status( redundancy["Name"], redundancy, chassis_instance["Readings"] )

    return sensor_list

def get_discrete_status( name, object, readings ):
    """
    Builds the status reading based on the Status object

    Args:
        name: The name to apply to the reading
        object: The object to parse
        readings: The list of readings to update
    """

    if "Status" not in object:
        # Do not produce a dummy reading if Status is not found
        return
    state, health = get_status( object )

    reading = {
        "Name": name,
        "Reading": state,
        "Units": None,
        "State": state,
        "Health": health,
        "LowerFatal": None,
        "LowerCritical": None,
        "LowerCaution": None,
        "UpperCaution": None,
        "UpperCritical": None,
        "UpperFatal": None,
    }

    readings.append( reading )

def get_analog_status_full( name, object, readings ):
    """
    Builds a full analog reading based on the the contents of an object

    Args:
        name: The name to apply to the reading
        object: The object to parse
        readings: The list of readings to update
    """

    state, health = get_status( object )
    units = None

    if "ReadingCelsius" in object:
        reading_val = object["ReadingCelsius"]
        units = "C"
    elif "ReadingVolts" in object:
        reading_val = object["ReadingVolts"]
        units = "V"
    elif "Reading" in object:
        reading_val = object["Reading"]
        if "ReadingUnits" in object:
            if object["ReadingUnits"] == "Percent":
                units = "%"
            else:
                units = object["ReadingUnits"]
    else:
        reading_val = None

    if reading_val is None:
        reading_val = state

    reading = {
        "Name": name,
        "Reading": reading_val,
        "Units": units,
        "State": state,
        "Health": health,
        "LowerFatal": object.get( "LowerThresholdFatal", None ),
        "LowerCritical": object.get( "LowerThresholdCritical", None ),
        "LowerCaution": object.get( "LowerThresholdNonCritical", None ),
        "UpperCaution": object.get( "UpperThresholdNonCritical", None ),
        "UpperCritical": object.get( "UpperThresholdCritical", None ),
        "UpperFatal": object.get( "UpperThresholdFatal", None ),
    }

    readings.append( reading )

def get_analog_status_small( name, field, units, object, readings ):
    """
    Builds an analog reading without thresholds based on a single field

    Args:
        name: The name to apply to the reading
        field: The field with the reading
        units: The units of measure for the reading
        object: The object to parse
        readings: The list of readings to update
    """

    if field not in object:
        return

    reading = {
        "Name": name + " " + field,
        "Reading": object[field],
        "Units": units,
        "State": None,
        "Health": None,
        "LowerFatal": None,
        "LowerCritical": None,
        "LowerCaution": None,
        "UpperCaution": None,
        "UpperCritical": None,
        "UpperFatal": None,
    }

    readings.append( reading )

def get_status( object ):
    """
    Gets the lower Status information

    Args:
        object: The object containing Status

    Returns:
        The state within Status (None if not found)
        The health within Status (None if not found)
    """

    state = None
    health = None

    if "Status" in object:
        state = object["Status"].get( "State", None )
        health = object["Status"].get( "Health", None )

    return state, health

def print_sensors( sensor_list ):
    """
    Prints the sensor list into a table

    Args:
        sensor_list: The sensor list to print
    """

    sensor_line_format = "  {:25s} | {:10s} | {:8s} | {:8s} | {:8s} | {:8s} | {:8s} | {:8s} | {:8s}"

    # Go through each chassis object in the list
    for chassis in sensor_list:

        print( "Chassis '" + chassis["ChassisName"] + "' Status" )
        print( sensor_line_format.format( "Sensor", "Reading", "Health", "LF", "LC", "LNC", "UNC", "UC", "UF" ) )

        # Go through each reading in the chassis
        for reading in chassis["Readings"]:

            # Sanitize the data for printing; use a new object to not modify the original reading data
            reading_pr = {}
            for item in reading:
                if item == "Name":
                    reading_pr["Name"] = reading["Name"][:25]
                elif item == "Reading":
                    if reading["Reading"] is None:
                        reading_pr["Reading"] = "Unknown"
                    else:
                        reading_pr["Reading"] = str( reading["Reading"] )
                        if reading["Units"] is not None:
                            reading_pr["Reading"] = reading_pr["Reading"] + reading["Units"]
                    reading_pr["Reading"] = reading_pr["Reading"][:10]
                elif item == "Units":
                    if reading["Units"] is None:
                        reading_pr["Units"] = ""
                else:
                    if reading[item] is None:
                        reading_pr[item] = "N/A"
                    else:
                        reading_pr[item] = str( reading[item] )

            # Print it
            print( sensor_line_format.format( reading_pr["Name"], reading_pr["Reading"], reading_pr["Health"],
                reading_pr["LowerFatal"], reading_pr["LowerCritical"], reading_pr["LowerCaution"],
                reading_pr["UpperCaution"], reading_pr["UpperCritical"], reading_pr["UpperFatal"] ) )
        print( "" )
