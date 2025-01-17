#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Thermal Equipment Module

File : thermal_equipment.py

Brief : This file contains the definitions and functionalities for interacting
        with the thermal equipment for a given Redfish service
"""

from .collections import get_collection_ids
from .messages import verify_response
from enum import Enum


class RedfishThermalEquipmentNotFoundError(Exception):
    """
    Raised when the requested thermal equipment is not represented in the service
    """

    pass


class RedfishThermalEquipmentComponentNotFoundError(Exception):
    """
    Raised when the requested thermal equipment does not contain the desired component
    """

    pass


class thermal_equipment_types(Enum):
    """
    Types of thermal equipment that can be managed
    """

    CDU = "CDU"
    HEAT_EXCHANGER = "HeatExchanger"
    IMMERSION_UNIT = "ImmersionUnit"

    def __str__(self):
        return self.value

    @property
    def plural(self):
        return self.value + "s"


class thermal_equipment_component_types(Enum):
    """
    Types of components found on thermal equipment
    """

    PRIMARY_CONNECTOR = "PrimaryCoolantConnector"
    SECONDARY_CONNECTOR = "SecondaryCoolantConnector"
    PUMP = "Pump"
    FILTER = "Filter"
    RESERVOIR = "Reservoir"

    def __str__(self):
        return self.value

    @property
    def plural(self):
        return self.value + "s"

    @property
    def short_name(self):
        if self.value == "PrimaryCoolantConnector":
            return "Primary"
        if self.value == "SecondaryCoolantConnector":
            return "Secondary"
        return self.value


def get_thermal_equipment_ids(context):
    """
    Finds the thermal equipment and returns all thermal equipment identifiers

    Args:
        context: The Redfish client object with an open session

    Returns:
        A dictionary containing lists of identifiers for each type of thermal equipment
    """

    # Get the service root to find the power equipment
    service_root = context.get("/redfish/v1/")
    if "ThermalEquipment" not in service_root.dict:
        # No thermal equipment
        raise RedfishThermalEquipmentNotFoundError("The service does not contain any thermal equipment")

    # Get the thermal equipment sets
    thermal_equipment = context.get(service_root.dict["ThermalEquipment"]["@odata.id"])
    verify_response(thermal_equipment)

    # Build up the lists of identifiers from the thermal equipment
    thermal_equipment_identifiers = {}
    for equip_type in thermal_equipment_types:
        thermal_equipment_identifiers[equip_type.plural] = []
        if equip_type.plural in thermal_equipment.dict:
            # Get the collection identifiers for this thermal equipment type
            thermal_equipment_identifiers[equip_type.plural] = get_collection_ids(
                context, thermal_equipment.dict[equip_type.plural]["@odata.id"]
            )

    return thermal_equipment_identifiers


def get_thermal_equipment_summary(context):
    """
    Gets a summary of all thermal equipment

    Args:
        context: The Redfish client object with an open session

    Returns:
        A dictionary containing lists of summary info for each type of thermal equipment
    """

    # Get the equipment identifiers
    thermal_equipment_identifiers = get_thermal_equipment_ids(context)

    # Build up the lists of summary info from the discovered identifiers
    thermal_equipment_summary = {}
    for equipment_type in thermal_equipment_types:
        thermal_equipment_summary[equipment_type.plural] = []
        if equipment_type.plural in thermal_equipment_identifiers:
            for equip in thermal_equipment_identifiers[equipment_type.plural]:
                # Get the equipment info
                equipment = get_thermal_equipment(context, equipment_type, equip)
                summary = {
                    "Id": equipment["Info"].dict.get("Id"),
                    "Model": equipment["Info"].dict.get("Model"),
                    "SerialNumber": equipment["Info"].dict.get("SerialNumber"),
                    "State": equipment["Info"].dict.get("Status", {}).get("State"),
                    "Health": equipment["Info"].dict.get("Status", {}).get("Health"),
                }
                thermal_equipment_summary[equipment_type.plural].append(summary)

    return thermal_equipment_summary


def print_thermal_equipment_summary(thermal_equipment_summary):
    """
    Prints the thermal equipment summary into a table

    Args:
        thermal_equipment_summary: The thermal equipment summary to print
    """

    summary_line_format = "  {:16s} | {:16s} | {:16s} | {:12s} | {:8s}"

    for equipment_type in thermal_equipment_summary:
        if len(thermal_equipment_summary[equipment_type]):
            print(equipment_type)
            print(summary_line_format.format("Id", "Model", "Serial Number", "State", "Health"))
            for equipment in thermal_equipment_summary[equipment_type]:
                print(
                    summary_line_format.format(
                        equipment["Id"] if equipment["Id"] else "",
                        equipment["Model"] if equipment["Model"] else "",
                        equipment["SerialNumber"] if equipment["SerialNumber"] else "",
                        equipment["State"] if equipment["State"] else "",
                        equipment["Health"] if equipment["Health"] else "",
                    )
                )
            print("")


def get_thermal_equipment(
    context,
    thermal_equipment_type,
    thermal_equipment_id=None,
    get_metrics=False,
    get_primary_connectors=False,
    get_secondary_connectors=False,
    get_pumps=False,
    get_filters=False,
    get_reservoirs=False,
    get_leak_detection=False,
    get_leak_detectors=False,
):
    """
    Finds a therma equipment matching the given identifier and returns its resource

    Args:
        context: The Redfish client object with an open session
        thermal_equipment_type: The thermal equipment type to get; see thermal_equipment_types enumeration
        thermal_equipment_id: The thermal equipment to locate; if None, perform on the only thermal equipment
        get_metrics: Indicates if the metrics should be returned
        get_primary_connectors: Indicates if the primary connectors should be returned
        get_secondary_connectors: Indicates if the secondary connectors should be returned
        get_pumps: Indicates if the pumps should be returned
        get_filters: Indicates if the filters should be returned
        get_reservoirs: Indicates if the reservoirs should be returned
        get_leak_detection: Indicates if the leak detection info should be returned
        get_leak_detectors: Indicates if the leak detectors should be returned

    Returns:
        A dictionary containing the thermal equipment resource and optional subordinate resources
    """

    thermal_equipment_uri_pattern = "/redfish/v1/ThermalEquipment/" + thermal_equipment_type.plural + "/{}"
    avail_thermal_equipment = None
    thermal_equipment = {"Info": None}
    if get_leak_detectors:
        # Getting leak detectors relies on getting the overall leak detection
        get_leak_detection = True

    # If given an identifier, get the thermal equipment directly
    if thermal_equipment_id is not None:
        thermal_equipment["Info"] = context.get(thermal_equipment_uri_pattern.format(thermal_equipment_id))
    # No identifier given; see if there's exactly one member
    else:
        all_thermal_equipment = get_thermal_equipment_ids(context)
        if thermal_equipment_type.plural not in all_thermal_equipment:
            raise RedfishThermalEquipmentNotFoundError(
                "The service does not contain any {}".format(thermal_equipment_type.plural)
            )
        avail_thermal_equipment = all_thermal_equipment[thermal_equipment_type.plural]
        if len(avail_thermal_equipment) == 1:
            thermal_equipment["Info"] = context.get(thermal_equipment_uri_pattern.format(avail_thermal_equipment[0]))
        else:
            raise RedfishThermalEquipmentNotFoundError(
                "The service contains multiple {}; a target thermal equipment needs to be specified: {}".format(
                    thermal_equipment_type.plural, ", ".join(avail_thermal_equipment)
                )
            )

    # Check the response and return the manager if the response is good
    if thermal_equipment["Info"].status == 404:
        if avail_thermal_equipment is None:
            all_equipment = get_thermal_equipment_ids(context)
            if thermal_equipment_type.plural not in all_equipment:
                raise RedfishThermalEquipmentNotFoundError(
                    "The service does not contain any {}".format(thermal_equipment_type.plural)
                )
            avail_equipment = all_equipment[thermal_equipment_type.plural]
        raise RedfishThermalEquipmentNotFoundError(
            "The service does not contain any {} called {}; valid {}: {}".format(
                thermal_equipment_type.plural,
                thermal_equipment_id,
                thermal_equipment_type.plural,
                ", ".join(avail_equipment),
            )
        )
    verify_response(thermal_equipment["Info"])

    # Get each of the subordinate resources requested by the caller
    resource_grabber = [
        {"Property": "EnvironmentMetrics", "Parameter": get_metrics, "Collection": False, "SubResource": "Info"},
        {
            "Property": "PrimaryCoolantConnectors",
            "Parameter": get_primary_connectors,
            "Collection": True,
            "SubResource": "Info",
        },
        {
            "Property": "SecondaryCoolantConnectors",
            "Parameter": get_secondary_connectors,
            "Collection": True,
            "SubResource": "Info",
        },
        {"Property": "Pumps", "Parameter": get_pumps, "Collection": True, "SubResource": "Info"},
        {"Property": "Filters", "Parameter": get_filters, "Collection": True, "SubResource": "Info"},
        {"Property": "Reservoirs", "Parameter": get_reservoirs, "Collection": True, "SubResource": "Info"},
        {"Property": "LeakDetection", "Parameter": get_leak_detection, "Collection": False, "SubResource": "Info"},
        {
            "Property": "LeakDetectors",
            "Parameter": get_leak_detectors,
            "Collection": True,
            "SubResource": "LeakDetection",
        },
    ]
    for resource in resource_grabber:
        thermal_equipment[resource["Property"]] = None
        if resource["Parameter"] and resource["Property"] in thermal_equipment[resource["SubResource"]].dict:
            if resource["Collection"]:
                thermal_equipment[resource["Property"]] = []
                collection = get_collection_ids(
                    context, thermal_equipment[resource["SubResource"]].dict[resource["Property"]]["@odata.id"]
                )
                for member_id in collection:
                    member = context.get(
                        thermal_equipment[resource["SubResource"]].dict[resource["Property"]]["@odata.id"]
                        + "/"
                        + member_id
                    )
                    verify_response(member)
                    thermal_equipment[resource["Property"]].append(member)
            else:
                thermal_equipment[resource["Property"]] = context.get(
                    thermal_equipment[resource["SubResource"]].dict[resource["Property"]]["@odata.id"]
                )
                verify_response(thermal_equipment[resource["Property"]])

    return thermal_equipment


def print_thermal_equipment(thermal_equipment):
    """
    Prints the thermal equipment info

    Args:
        thermal_equipment: The thermal equipment info to print
    """

    thermal_equipment_line_format = "  {}: {}"
    print("{} {} Info".format(thermal_equipment["Info"].dict["EquipmentType"], thermal_equipment["Info"].dict["Id"]))

    print("")
    thermal_equipment_properties = [
        "Status",
        "EquipmentType",
        "Model",
        "Manufacturer",
        "PartNumber",
        "SerialNumber",
        "Version",
        "FirmwareVersion",
        "ProductionDate",
        "AssetTag",
        "UserLabel",
        "CoolingCapacityWatts",
        "Coolant",
    ]
    for property in thermal_equipment_properties:
        if property in thermal_equipment["Info"].dict:
            prop_val = thermal_equipment["Info"].dict[property]
            if isinstance(prop_val, list):
                prop_val = ", ".join([i for i in prop_val if i is not None])
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format(prop_val.get("State", "N/A"), prop_val.get("Health", "N/A"))
            elif property == "Coolant":
                prop_val = get_coolant_string(prop_val)
            print(thermal_equipment_line_format.format(property, prop_val))
    if thermal_equipment["EnvironmentMetrics"]:
        thermal_equipment_properties = [
            ("PowerWatts", "Power", "W"),
            ("EnergykWh", "Energy", "kWh"),
            ("TemperatureCelsius", "Temperature", "C"),
            ("HumidityPercent", "Humidity", "%"),
            ("PowerLoadPercent", "PowerLoad", "%"),
            ("AbsoluteHumidity", "AbsoluteHumidity", "g/m^3"),
        ]
        for property in thermal_equipment_properties:
            if property[0] in thermal_equipment["EnvironmentMetrics"].dict:
                if thermal_equipment["EnvironmentMetrics"].dict[property[0]]["Reading"] is None:
                    prop_val = "Unavailable"
                else:
                    prop_val = (
                        str(thermal_equipment["EnvironmentMetrics"].dict[property[0]]["Reading"]) + " " + property[2]
                    )
                print(thermal_equipment_line_format.format(property[1], prop_val))
    if thermal_equipment["LeakDetection"]:
        if "LeakDetectorGroups" in thermal_equipment["LeakDetection"].dict:
            for i, group in enumerate(thermal_equipment["LeakDetection"].dict["LeakDetectorGroups"]):
                group_name = "Leak Detection Group {}".format(i)
                if "GroupName" in group:
                    group_name = group["GroupName"]
                prop_val = group.get("Status", {}).get("Health", "OK")
                if "HumidityPercent" in group:
                    prop_val = prop_val + ", Humidity: {} %".format(
                        str(group.get("HumidityPercent", {}).get("Reading", "---"))
                    )
                print(thermal_equipment_line_format.format(group_name, prop_val))
    print("")


def get_thermal_equipment_component(
    context, thermal_equipment_type, thermal_equipment_component_type, thermal_equipment_id=None, component_id=None
):
    """
    Finds a component for an instance of thermal equipment and returns its resource

    Args:
        context: The Redfish client object with an open session
        thermal_equipment_type: The thermal equipment type to get; see thermal_equipment_types enumeration
        thermal_equipment_component_type: The component type to get; see thermal_equipment_component_types enumeration
        thermal_equipment_id: The thermal equipment to locate; if None, perform on the only thermal equipment
        component_id: The component to locate; if None, perform on the only component

    Returns:
        The component resource
    """

    # Get the thermal equipment
    thermal_equipment = get_thermal_equipment(context, thermal_equipment_type, thermal_equipment_id)

    # Check that the thermal equipment has the desired component type
    if thermal_equipment_component_type.plural not in thermal_equipment["Info"].dict:
        raise RedfishThermalEquipmentComponentNotFoundError(
            "{} {} does not contain any {}".format(
                thermal_equipment_type.plural,
                thermal_equipment["Info"].dict["Id"],
                thermal_equipment_component_type.plural,
            )
        )

    thermal_equipment_component_uri_pattern = (
        thermal_equipment["Info"].dict[thermal_equipment_component_type.plural]["@odata.id"] + "/{}"
    )
    avail_component = None

    # If given an identifier, get the outlet or circuit directly
    if component_id is not None:
        component = context.get(thermal_equipment_component_uri_pattern.format(component_id))
    # No identifier given; see if there's exactly one member
    else:
        avail_component = get_collection_ids(
            context, thermal_equipment["Info"].dict[thermal_equipment_component_type.plural]["@odata.id"]
        )
        if len(avail_component) == 1:
            component = context.get(thermal_equipment_component_uri_pattern.format(avail_component[0]))
        else:
            raise RedfishThermalEquipmentComponentNotFoundError(
                "{} {} contains multiple {}; a target component needs to be specified: {}".format(
                    thermal_equipment_type.plural,
                    thermal_equipment["Info"].dict["Id"],
                    thermal_equipment_component_type.plural,
                    ", ".join(avail_component),
                )
            )

    # Check the response and return the manager if the response is good
    if component.status == 404:
        if avail_component is None:
            avail_component = get_collection_ids(
                context, thermal_equipment["Info"].dict[thermal_equipment_component_type.plural]["@odata.id"]
            )
        raise RedfishThermalEquipmentNotFoundError(
            "{} {} does not contain any {} called {}; valid {}: {}".format(
                thermal_equipment_type.plural,
                thermal_equipment["Info"].dict["Id"],
                thermal_equipment_component_type.plural,
                component_id,
                thermal_equipment_component_type.plural,
                ", ".join(avail_component),
            )
        )
    verify_response(component)
    return component


def print_thermal_equipment_component(component):
    """
    Prints the component info

    Args:
        component: The component to print
    """

    component_line_format = "  {}: {}"

    if "/PrimaryCoolantConnectors/" in component.dict["@odata.id"]:
        print("Primary Connector {} Info".format(component.dict["Id"]))
    elif "/SecondaryCoolantConnectors/" in component.dict["@odata.id"]:
        print("Secondary Connector {} Info".format(component.dict["Id"]))
    else:
        print("{} {} Info".format(component.dict["@odata.type"].split(".")[-1], component.dict["Id"]))

    print("")
    # Display the simple properties
    component_properties = [
        "Status",
        "FluidLevelStatus",
        "CoolantConnectorType",
        "ReservoirType",
        "PumpType",
        "Model",
        "Manufacturer",
        "PartNumber",
        "SerialNumber",
        "Version",
        "FirmwareVersion",
        "ProductionDate",
        "AssetTag",
        "UserLabel",
        "Coolant",
        "RatedFlowLitersPerMinute",
        "RatedFlowPressurekPa",
        "RatedPressurekPa",
        "ServicedDate",
        "ServiceHours",
        "RatedServiceHours",
        "Replaceable",
        "HotPluggable",
        "CapacityLiters",
    ]
    for property in component_properties:
        if property in component.dict:
            prop_val = component.dict[property]
            if isinstance(prop_val, list):
                prop_val = ", ".join([i for i in prop_val if i is not None])
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format(prop_val.get("State", "N/A"), prop_val.get("Health", "N/A"))
            elif property == "Coolant":
                prop_val = prop_val = get_coolant_string(prop_val)
            elif property == "FluidLevelStatus":
                if "FluidLevelPercent" in component.dict:
                    prop_val = (
                        prop_val + " (" + str(component.dict.get("FluidLevelPercent", {}).get("Reading", "---")) + " %)"
                    )
            else:
                prop_val = str(prop_val)
            print(component_line_format.format(property, prop_val))
    # Display the embedded metrics
    component_properties = [
        ("FlowLitersPerMinute", "Flow", "L/min"),
        ("HeatRemovedkW", "HeatRemoved", "kW"),
        ("SupplyTemperatureCelsius", "SupplyTemperature", "C"),
        ("ReturnTemperatureCelsius", "ReturnTemperature", "C"),
        ("DeltaTemperatureCelsius", "DeltaTemperature", "C"),
        ("SupplyPressurekPa", "SupplyPressure", "kPa"),
        ("ReturnPressurekPa", "ReturnPressure", "kPa"),
        ("DeltaPressurekPa", "DeltaPressure", "kPa"),
        ("PumpSpeedPercent", "PumpSpeed", "%"),
    ]
    for property in component_properties:
        if property[0] in component.dict:
            if component.dict[property[0]]["Reading"] is None:
                prop_val = "Unavailable"
            else:
                prop_val = str(component.dict[property[0]]["Reading"]) + " " + property[2]
            print(component_line_format.format(property[1], prop_val))
    # Display compounded embedded metrics
    component_properties = [
        ("Temperature", "Celsius", "C"),
        ("Pressure", "kPa", "kPa"),
    ]
    for property in component_properties:
        compound_val = []
        for measurement_point in ["Supply", "Return", "Delta"]:
            prop_name = measurement_point + property[0] + property[1]
            if prop_name in component.dict:
                if component.dict[prop_name]["Reading"] is None:
                    prop_val = "Unavailable"
                else:
                    prop_val = str(component.dict[prop_name]["Reading"]) + " " + property[2]
                compound_val.append(measurement_point + " " + prop_val)
        if compound_val:
            print(component_line_format.format(property[0], ", ".join(compound_val)))
    print("")


def print_thermal_equipment_component_summary(thermal_equipment, component_type, print_heading):
    """
    Prints the component summary for an instance of thermal equipment

    Args:
        thermal_equipment: The thermal equipment info to print
        component_type: The type of component info to print
        print_heading: Indicates if the tabling heading should be printed
    """

    if not thermal_equipment[component_type.plural]:
        if print_heading:
            print(
                "{} {} does not contain any {}".format(
                    thermal_equipment["Info"].dict["EquipmentType"],
                    thermal_equipment["Info"].dict["Id"],
                    component_type.plural,
                )
            )
        return

    if print_heading:
        print(
            "{} {} {}".format(
                thermal_equipment["Info"].dict["EquipmentType"],
                thermal_equipment["Info"].dict["Id"],
                component_type.plural,
            )
        )
        print("")

    if component_type == thermal_equipment_component_types.PUMP:
        component_line_format = "  {:16s} | {:12s} | {:12s} | {:12s} | {:12s}"
        print(
            component_line_format.format(
                component_type.short_name + " Id",
                "Type",
                "State",
                "Health",
                "Speed (%)",
            )
        )
        for item in thermal_equipment[component_type.plural]:
            type = str(item.dict.get("PumpType", "---"))
            state = str(item.dict.get("Status", {}).get("State", "---"))
            health = str(item.dict.get("Status", {}).get("Health", "---"))
            speed = str(item.dict.get("PumpSpeedPercent", {}).get("Reading", "---"))
            print(component_line_format.format(item.dict["Id"], type, state, health, speed))
    elif component_type == thermal_equipment_component_types.FILTER:
        component_line_format = "  {:16s} | {:12s} | {:12s} | {:25s} | {:12s}"
        print(
            component_line_format.format(
                component_type.short_name + " Id",
                "State",
                "Health",
                "Serviced Date",
                "Service Hours",
            )
        )
        for item in thermal_equipment[component_type.plural]:
            state = str(item.dict.get("Status", {}).get("State", "---"))
            health = str(item.dict.get("Status", {}).get("Health", "---"))
            serviced_date = str(item.dict.get("ServicedDate", "---"))
            service_hours = str(item.dict.get("ServiceHours", "---"))
            print(component_line_format.format(item.dict["Id"], state, health, serviced_date, service_hours))
    elif component_type == thermal_equipment_component_types.RESERVOIR:
        component_line_format = "  {:16s} | {:12s} | {:12s} | {:12s} | {:20s}"
        print(
            component_line_format.format(
                component_type.short_name + " Id",
                "Type",
                "State",
                "Health",
                "Fluid Status",
            )
        )
        for item in thermal_equipment[component_type.plural]:
            type = str(item.dict.get("ReservoirType", "---"))
            state = str(item.dict.get("Status", {}).get("State", "---"))
            health = str(item.dict.get("Status", {}).get("Health", "---"))
            fluid_status = str(item.dict.get("FluidLevelStatus", "---"))
            if "FluidLevelPercent" in item.dict:
                fluid_status = (
                    fluid_status + " (" + str(item.dict.get("FluidLevelPercent", {}).get("Reading", "---")) + " %)"
                )
            print(component_line_format.format(item.dict["Id"], type, state, health, fluid_status))
    else:
        component_line_format = "  {:16s} | {:12s} | {:12s} | {:14s} | {:12s} | {:14s}"
        print(
            component_line_format.format(
                component_type.short_name + " Id",
                "Flow (L/min)",
                "Supply T (C)",
                "Supply P (kPa)",
                "Return T (C)",
                "Return P (kPa)",
            )
        )
        for item in thermal_equipment[component_type.plural]:
            flow = str(item.dict.get("FlowLitersPerMinute", {}).get("Reading", "---"))
            supply_temp = str(item.dict.get("SupplyTemperatureCelsius", {}).get("Reading", "---"))
            supply_pressure = str(item.dict.get("SupplyPressurekPa", {}).get("Reading", "---"))
            return_temp = str(item.dict.get("ReturnTemperatureCelsius", {}).get("Reading", "---"))
            return_pressure = str(item.dict.get("ReturnPressurekPa", {}).get("Reading", "---"))
            print(
                component_line_format.format(
                    item.dict["Id"], flow, supply_temp, supply_pressure, return_temp, return_pressure
                )
            )
    print("")


def print_thermal_equipment_leak_detector_summary(thermal_equipment, print_heading):
    """
    Prints the leak detector summary for an instance of thermal equipment

    Args:
        thermal_equipment: The thermal equipment info to print
        print_heading: Indicates if the tabling heading should be printed
    """

    if not thermal_equipment["LeakDetection"]:
        if print_heading:
            print(
                "{} {} does not contain any leak detection".format(
                    thermal_equipment["Info"].dict["EquipmentType"],
                    thermal_equipment["Info"].dict["Id"],
                )
            )
        return

    if print_heading:
        print(
            "{} {} Leak Detection".format(
                thermal_equipment["Info"].dict["EquipmentType"],
                thermal_equipment["Info"].dict["Id"],
            )
        )
        print("")

    detector_line_format = "  {:16s} | {:30s} | {:12s}"

    # Print info from leak detector groups
    grouped_detectors = []
    if "LeakDetectorGroups" in thermal_equipment["LeakDetection"].dict:
        for i, group in enumerate(thermal_equipment["LeakDetection"].dict["LeakDetectorGroups"]):
            group_name = "Leak Detection Group {}".format(i)
            if "GroupName" in group:
                group_name = group["GroupName"]
            prop_val = group.get("Status", {}).get("Health", "OK")
            if "HumidityPercent" in group:
                prop_val = prop_val + ", Humidity: {} %".format(
                    str(group.get("HumidityPercent", {}).get("Reading", "---"))
                )
            print("{}: {}".format(group_name, prop_val))
            print(detector_line_format.format("Detector Id", "Name", "State"))
            if "Detectors" in group:
                for j, detector in enumerate(group["Detectors"]):
                    detector_id = detector.get("DataSourceUri", "").split("/")[-1]
                    if "DataSourceUri" in detector:
                        grouped_detectors.append(detector["DataSourceUri"])
                    print(
                        detector_line_format.format(
                            detector_id, detector.get("DeviceName", ""), detector.get("DetectorState", "N/A")
                        )
                    )
            print("")

    # Find any detectors that do not belong to groups and print their info
    non_grouped_detectors = []
    if thermal_equipment["LeakDetectors"]:
        for detector in thermal_equipment["LeakDetectors"]:
            if detector.dict["@odata.id"] not in grouped_detectors:
                non_grouped_detectors.append(detector)
    if non_grouped_detectors:
        print("Other Leak Detectors")
        print(detector_line_format.format("Detector Id", "Name", "State"))
        for detector in non_grouped_detectors:
            print(
                detector_line_format.format(
                    detector.dict["Id"], detector.dict["Name"], detector.dict.get("DetectorState", "N/A")
                )
            )
        print("")


def get_coolant_string(coolant):
    """
    Builds a string based on the contents of the common coolant object

    Args:
        coolant: The coolant object to parse

    Returns:
        A string of the coolant information
    """

    coolant_info = []
    if "CoolantType" in coolant:
        coolant_info.append(str(coolant["CoolantType"]))
    if "AdditivePercent" in coolant and "AdditiveName" in coolant:
        coolant_info.append("{} % {}".format(coolant["AdditivePercent"], coolant["AdditiveName"]))
    if "SpecificHeatkJoulesPerKgK" in coolant:
        coolant_info.append("Specific Heat: {} kJ/kg/K".format(coolant["SpecificHeatkJoulesPerKgK"]))
    if "DensityKgPerCubicMeter" in coolant:
        coolant_info.append("Density: {} kg/m3".format(coolant["DensityKgPerCubicMeter"]))
    return ", ".join(coolant_info)
