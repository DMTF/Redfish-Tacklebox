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
    Walks a Redfish service for sensor information

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all sensor readings
    """

    sensor_list = []

    # Get the service root to find the chassis collection
    service_root = context.get( "/redfish/v1/" )
    if "Chassis" not in service_root.dict:
        # No chassis collection
        return sensor_list

    # Get the chassis collection and iterate through its collection
    chassis_col = context.get( service_root.dict["Chassis"]["@odata.id"] )
    for chassis_member in chassis_col.dict["Members"]:
        chassis = context.get( chassis_member["@odata.id"] )

        # Get the chassis status
        chassis_instance = {
            "ChassisName": chassis.dict["Id"],
            "Readings": []
        }
        sensor_list.append( chassis_instance )
        get_discrete_status( "State", chassis.dict, chassis_instance["Readings"] )

        # If the chassis contains any of the newer power/thermal models, scan based on the common sensor model
        if "EnvironmentMetrics" in chassis.dict or "PowerSubsystem" in chassis.dict or "ThermalSubsystem" in chassis.dict:
            # Get readings from the EnvironmentMetrics resource if available
            if "EnvironmentMetrics" in chassis.dict:
                environment = context.get( chassis.dict["EnvironmentMetrics"]["@odata.id"] )
                get_excerpt_status( chassis_instance["ChassisName"], "TemperatureCelsius", "Cel", environment.dict, chassis_instance["Readings"] )
                get_excerpt_status( chassis_instance["ChassisName"], "HumidityPercent", "%", environment.dict, chassis_instance["Readings"] )
                get_excerpt_status( chassis_instance["ChassisName"], "PowerWatts", "W", environment.dict, chassis_instance["Readings"] )
                get_excerpt_status( chassis_instance["ChassisName"], "EnergykWh", "kW.h", environment.dict, chassis_instance["Readings"] )
                get_excerpt_status( chassis_instance["ChassisName"], "PowerLoadPercent", "%", environment.dict, chassis_instance["Readings"] )
                get_excerpt_status( chassis_instance["ChassisName"], "DewPointCelsius", "Cel", environment.dict, chassis_instance["Readings"] )

            # Get readings from the PowerSubsystem resource if available
            if "PowerSubsystem" in chassis.dict:
                power = context.get( chassis.dict["PowerSubsystem"]["@odata.id"] )

                # Add information for each power supply reported
                if "PowerSupplies" in power.dict:
                    power_supplies = context.get( power.dict["PowerSupplies"]["@odata.id"] )
                    for power_supply_member in power_supplies.dict["Members"]:
                        power_supply = context.get( power_supply_member["@odata.id"] )
                        power_supply_name = "Power Supply " + power_supply.dict["Id"]
                        get_discrete_status( power_supply_name + " State", power_supply.dict, chassis_instance["Readings"] )
                        if "Metrics" in power_supply.dict:
                            metrics = context.get( power_supply.dict["Metrics"]["@odata.id"] )
                            get_excerpt_status( power_supply_name, "InputVoltage", "V", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "InputCurrentAmps", "A", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "InputPowerWatts", "W", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "EnergykWh", "kW.h", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "FrequencyHz", "Hz", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "OutputPowerWatts", "W", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "RailVoltage", "V", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "RailCurrentAmps", "A", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "RailPowerWatts", "W", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "TemperatureCelsius", "Cel", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( power_supply_name, "FanSpeedPercent", "%", metrics.dict, chassis_instance["Readings"] )

                # Add information for each battery reported
                if "Batteries" in power.dict:
                    batteries = context.get( power.dict["Batteries"]["@odata.id"] )
                    for battery_member in batteries.dict["Members"]:
                        battery = context.get( battery_member["@odata.id"] )
                        battery_name = "Battery " + battery.dict["Id"]
                        get_discrete_status( battery_name + " State", battery.dict, chassis_instance["Readings"] )
                        get_excerpt_status( battery_name, "StateOfHealthPercent", "%", battery.dict, chassis_instance["Readings"])
                        if "Metrics" in battery.dict:
                            metrics = context.get( battery.dict["Metrics"]["@odata.id"] )
                            get_excerpt_status( battery_name, "InputVoltage", "V", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "InputCurrentAmps", "A", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "OutputVoltages", "V", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "OutputCurrentAmps", "A", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "StoredEnergyWattHours", "W.h", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "StoredChargeAmpHours", "A.h", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "TemperatureCelsius", "Cel", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "ChargePercent", "%", metrics.dict, chassis_instance["Readings"] )
                            get_excerpt_status( battery_name, "CellVoltages", "V", metrics.dict, chassis_instance["Readings"] )

                # Add information for each of the redundancy groups reported
                if "PowerSupplyRedundancy" in power.dict:
                    for i, redundancy in enumerate( power.dict["PowerSupplyRedundancy"] ):
                        get_discrete_status( "Power Supply Redundancy " + str( i ), redundancy, chassis_instance["Readings"] )

            # Get readings from the ThermalSubsystem resource if available
            if "ThermalSubsystem" in chassis.dict:
                thermal = context.get( chassis.dict["ThermalSubsystem"]["@odata.id"] )

                # Add overall thermal metrics
                if "ThermalMetrics" in thermal.dict:
                    metrics = context.get( thermal.dict["ThermalMetrics"]["@odata.id"] )
                    if "TemperatureSummaryCelsius" in metrics.dict:
                        get_excerpt_status( chassis_instance["ChassisName"], "Internal", "Cel", metrics.dict["TemperatureSummaryCelsius"], chassis_instance["Readings"] )
                        get_excerpt_status( chassis_instance["ChassisName"], "Intake", "Cel", metrics.dict["TemperatureSummaryCelsius"], chassis_instance["Readings"] )
                        get_excerpt_status( chassis_instance["ChassisName"], "Exhaust", "Cel", metrics.dict["TemperatureSummaryCelsius"], chassis_instance["Readings"] )
                        get_excerpt_status( chassis_instance["ChassisName"], "Ambient", "Cel", metrics.dict["TemperatureSummaryCelsius"], chassis_instance["Readings"] )

                # Add information for each fan reported
                if "Fans" in thermal.dict:
                    fans = context.get( thermal.dict["Fans"]["@odata.id"] )
                    for fan_member in fans.dict["Members"]:
                        fan = context.get( fan_member["@odata.id"] )
                        fan_name = "Fan " + fan.dict["Id"]
                        get_discrete_status( fan_name + " State", fan.dict, chassis_instance["Readings"] )
                        get_excerpt_status( fan_name, "SpeedPercent", "%", fan.dict, chassis_instance["Readings"])

                # Add information for each of the redundancy groups reported
                if "FanRedundancy" in thermal.dict:
                    for i, redundancy in enumerate( thermal.dict["FanRedundancy"] ):
                        get_discrete_status( "Fan Redundancy " + str( i ), redundancy, chassis_instance["Readings"] )

            # Get all sensor readings if available
            if "Sensors" in chassis.dict:
                sensors = context.get( chassis.dict["Sensors"]["@odata.id"] )
                for sensor_member in sensors.dict["Members"]:
                    sensor = context.get( sensor_member["@odata.id"] )
                    get_sensor_status( sensor.dict, chassis_instance["Readings"] )

        # Older power/thermal models
        else:
            # Get readings from the Power resource if available
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

            # Get readings from the Thermal resource if available
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
    Builds the status reading based on the Status property

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
        units = "Cel"
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
        "Name": "{} {}".format( name, field ),
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

def get_excerpt_status( name, field, units, object, readings ):
    """
    Builds an analog reading based on an excerpt

    Args:
        name: The name to apply to the reading
        field: The field with the reading
        units: The units of measure for the reading
        object: The object to parse
        readings: The list of readings to update
    """

    if field not in object:
        return

    if isinstance( object[field], list ):
        for i, item in enumerate( object[field] ):
            if "DataSourceUri" not in item:
                reading = {
                    "Name": "{} {} {}".format( name, field, i ),
                    "Reading": item.get( "Reading", None ),
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
    else:
        if "DataSourceUri" not in object[field]:
            reading = {
                "Name": "{} {}".format( name, field ),
                "Reading": object[field].get( "Reading", None ),
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

def get_sensor_status( sensor, readings ):
    """
    Builds an analog reading from a sensor

    Args:
        sensor: The sensor
        readings: The list of readings to update
    """

    state, health = get_status( sensor )
    units = sensor.get( "ReadingUnits", None )
    reading_val = sensor.get( "Reading", None )
    if reading_val is None:
        reading_val = state

    name = sensor.get( "Name", None )
    if name is None:
        name = "Sensor " + sensor["Id"]

    reading = {
        "Name": name,
        "Reading": reading_val,
        "Units": units,
        "State": state,
        "Health": health,
        "LowerFatal": sensor.get( "Thresholds", {} ).get( "LowerFatal", {} ).get( "Reading", None ),
        "LowerCritical": sensor.get( "Thresholds", {} ).get( "LowerCritical", {} ).get( "Reading", None ),
        "LowerCaution": sensor.get( "Thresholds", {} ).get( "LowerCaution", {} ).get( "Reading", None ),
        "UpperCaution": sensor.get( "Thresholds", {} ).get( "UpperCaution", {} ).get( "Reading", None ),
        "UpperCritical": sensor.get( "Thresholds", {} ).get( "UpperCritical", {} ).get( "Reading", None ),
        "UpperFatal": sensor.get( "Thresholds", {} ).get( "UpperFatal", {} ).get( "Reading", None ),
    }

    readings.append( reading )

def get_status( object ):
    """
    Gets the lower status information

    Args:
        object: The object containing the Status property

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
