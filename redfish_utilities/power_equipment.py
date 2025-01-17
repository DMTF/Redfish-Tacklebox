#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
PDU Module

File : power_equipment.py

Brief : This file contains the definitions and functionalities for interacting
        with the power equipment for a given Redfish service
"""

from .collections import get_collection_ids
from .messages import verify_response
from enum import Enum


class RedfishPowerEquipmentNotFoundError(Exception):
    """
    Raised when the requested power equipment is not represented in the service
    """

    pass


class RedfishPowerEquipmentElectricalNotFoundError(Exception):
    """
    Raised when the requested power equipment does not contain the desired electrical component
    """

    pass


class power_equipment_types(Enum):
    """
    Types of power equipment that can be managed
    """

    FLOOR_PDU = "FloorPDU"
    RACK_PDU = "RackPDU"
    SWITCHGEAR = "Switchgear"
    TRANSFER_SWITCH = "TransferSwitch"
    POWER_SHELF = "PowerShelf"
    ELECTRICAL_BUS = "ElectricalBus"

    def __str__(self):
        return self.value

    @property
    def plural(self):
        if self.value == "FloorPDU" or self.value == "RackPDU":
            return self.value + "s"
        if self.value == "TransferSwitch" or self.value == "ElectricalBus":
            return self.value + "es"
        if self.value == "PowerShelf":
            return "PowerShelves"
        return self.value


class power_equipment_electrical_types(Enum):
    """
    Types of electrical components found on power equipment
    """

    OUTLET = "Outlet"
    MAINS = "Mains"
    BRANCH = "Branch"
    FEEDER = "Feeder"
    SUBFEED = "Subfeed"

    def __str__(self):
        return self.value

    @property
    def plural(self):
        if self.value == "Mains":
            return self.value
        if self.value == "Branch":
            return self.value + "es"
        return self.value + "s"


voltage_type_strings = {
    "AC100To127V": "100 V to 127 V AC",
    "AC100To240V": "100 V to 240 V AC",
    "AC100To277V": "100 V to 277 V AC",
    "AC120V": "120 V AC",
    "AC200To240V": "200 V to 240 V AC",
    "AC200To277V": "200 V to 277 V AC",
    "AC208V": "208 V AC",
    "AC230V": "230 V AC",
    "AC240V": "240 V AC",
    "AC240AndDC380V": "240 V AC/380 V DC",
    "AC277V": "277 V AC",
    "AC277AndDC380V": "277 V AC/380 V DC",
    "AC400V": "400 V AC",
    "AC480V": "480 V AC",
    "DC48V": "48 V DC",
    "DC240V": "240 V DC",
    "DC380V": "380 V DC",
    "DCNeg48V": "-48 V DC",
}

phase_wiring_type_strings = {
    "OnePhase3Wire": "1 Phase, 3 Wire",
    "TwoPhase3Wire": "2 Phase, 3 Wire",
    "OneOrTwoPhase3Wire": "1 or 2 Phase, 3 Wire",
    "TwoPhase4Wire": "2 Phase, 4 Wire",
    "ThreePhase4Wire": "3 Phase, 4 Wire",
    "ThreePhase5Wire": "3 Phase, 5 Wire",
}

receptical_type_strings = {
    "BS_1363_Type_G": "BS 1363 Type G (250V; 13A)",
    "BusConnection": "Electrical bus connection",
    "CEE_7_Type_E": "CEE 7/7 Type E (250V; 16A)",
    "CEE_7_Type_F": "CEE 7/7 Type F (250V; 16A)",
    "IEC_60320_C13": "IEC C13 (250V; 10A or 15A)",
    "IEC_60320_C19": "IEC C19 (250V; 16A or 20A)",
    "NEMA_5_15R": "NEMA 5-15R (120V; 15A)",
    "NEMA_5_20R": "NEMA 5-20R (120V; 20A)",
    "NEMA_L5_20R": "NEMA L5-20R (120V; 20A)",
    "NEMA_L5_30R": "NEMA L5-30R (120V; 30A)",
    "NEMA_L6_20R": "NEMA L6-20R (250V; 20A)",
    "NEMA_L6_30R": "NEMA L6-30R (250V; 30A)",
    "SEV_1011_TYPE_12": "SEV 1011 Type 12 (250V; 10A)",
    "SEV_1011_TYPE_23": "SEV 1011 Type 23 (250V; 16A)",
}

plug_type_strings = {
    "California_CS8265": "California Standard CS8265 (Single-phase 250V; 50A; 2P3W)",
    "California_CS8365": "California Standard CS8365 (Three-phase 250V; 50A; 3P4W)",
    "Field_208V_3P4W_60A": "Field-wired; Three-phase 200-250V; 60A; 3P4W",
    "Field_400V_3P5W_32A": "Field-wired; Three-phase 200-240/346-415V; 32A; 3P5W",
    "IEC_60309_316P6": "IEC 60309 316P6 (Single-phase 200-250V; 16A; 1P3W; Blue, 6-hour)",
    "IEC_60309_332P6": "IEC 60309 332P6 (Single-phase 200-250V; 32A; 1P3W; Blue, 6-hour)",
    "IEC_60309_363P6": "IEC 60309 363P6 (Single-phase 200-250V; 63A; 1P3W; Blue, 6-hour)",
    "IEC_60309_460P9": "IEC 60309 460P9 (Three-phase 200-250V; 60A; 3P4W; Blue; 9-hour)",
    "IEC_60309_516P6": "IEC 60309 516P6 (Three-phase 200-240/346-415V; 16A; 3P5W; Red; 6-hour)",
    "IEC_60309_532P6": "IEC 60309 532P6 (Three-phase 200-240/346-415V; 32A; 3P5W; Red; 6-hour)",
    "IEC_60309_560P9": "IEC 60309 560P9 (Three-phase 120-144/208-250V; 60A; 3P5W; Blue; 9-hour)",
    "IEC_60309_563P6": "IEC 60309 563P6 (Three-phase 200-240/346-415V; 63A; 3P5W; Red; 6-hour)",
    "IEC_60320_C14": "IEC C14 (Single-phase 250V; 10A; 1P3W)",
    "IEC_60320_C20": "IEC C20 (Single-phase 250V; 16A; 1P3W)",
    "NEMA_5_15P": "NEMA 5-15P (Single-phase 125V; 15A; 1P3W)",
    "NEMA_5_20P": "NEMA 5-20P (Single-phase 125V; 20A; 1P3W)",
    "NEMA_6_15P": "NEMA 6-15P (Single-phase 250V; 15A; 2P3W)",
    "NEMA_6_20P": "NEMA 6-20P (Single-phase 250V; 20A; 2P3W)",
    "NEMA_L14_20P": "NEMA L14-20P (Split-phase 125/250V; 20A; 2P4W)",
    "NEMA_L14_30P": "NEMA L14-30P (Split-phase 125/250V; 30A; 2P4W)",
    "NEMA_L15_20P": "NEMA L15-20P (Three-phase 250V; 20A; 3P4W)",
    "NEMA_L15_30P": "NEMA L15-30P (Three-phase 250V; 30A; 3P4W)",
    "NEMA_L21_20P": "NEMA L21-20P (Three-phase 120/208V; 20A; 3P5W)",
    "NEMA_L21_30P": "NEMA L21-30P (Three-phase 120/208V; 30A; 3P5W)",
    "NEMA_L22_20P": "NEMA L22-20P (Three-phase 277/480V; 20A; 3P5W)",
    "NEMA_L22_30P": "NEMA L22-30P (Three-phase 277/480V; 30A; 3P5W)",
    "NEMA_L5_15P": "NEMA L5-15P (Single-phase 125V; 15A; 1P3W)",
    "NEMA_L5_20P": "NEMA L5-20P (Single-phase 125V; 20A; 1P3W)",
    "NEMA_L5_30P": "NEMA L5-30P (Single-phase 125V; 30A; 1P3W)",
    "NEMA_L6_15P": "NEMA L6-15P (Single-phase 250V; 15A; 2P3W)",
    "NEMA_L6_20P": "NEMA L6-20P (Single-phase 250V; 20A; 2P3W)",
    "NEMA_L6_30P": "NEMA L6-30P (Single-phase 250V; 30A; 2P3W)",
}

line_measurement_strings = {
    "Line1ToLine2": "L1-L2",
    "Line1ToNeutral": "L1-N",
    "Line2ToLine3": "L2-L3",
    "Line2ToNeutral": "L2-N",
    "Line3ToLine1": "L3-L1",
    "Line3ToNeutral": "L3-N",
    "Line1": "L1",
    "Line2": "L2",
    "Line3": "L3",
    "Neutral": "N",
}


def get_power_equipment_ids(context):
    """
    Finds the power equipment and returns all power equipment identifiers

    Args:
        context: The Redfish client object with an open session

    Returns:
        A dictionary containing lists of identifiers for each type of power equipment
    """

    # Get the service root to find the power equipment
    service_root = context.get("/redfish/v1/")
    if "PowerEquipment" not in service_root.dict:
        # No power equipment
        raise RedfishPowerEquipmentNotFoundError("The service does not contain any power equipment")

    # Get the power equipment sets
    power_equipment = context.get(service_root.dict["PowerEquipment"]["@odata.id"])
    verify_response(power_equipment)

    # Build up the lists of identifiers from the power equipment
    power_equipment_identifiers = {}
    for equip_type in power_equipment_types:
        power_equipment_identifiers[equip_type.plural] = []
        if equip_type.plural in power_equipment.dict:
            # Get the collection identifiers for this power equipment type
            power_equipment_identifiers[equip_type.plural] = get_collection_ids(
                context, power_equipment.dict[equip_type.plural]["@odata.id"]
            )

    return power_equipment_identifiers


def get_power_equipment_summary(context):
    """
    Gets a summary of all power equipment

    Args:
        context: The Redfish client object with an open session

    Returns:
        A dictionary containing lists of summary info for each type of power equipment
    """

    # Get the equipment identifiers
    power_equipment_identifiers = get_power_equipment_ids(context)

    # Build up the lists of summary info from the discovered identifiers
    power_equipment_summary = {}
    for equipment_type in power_equipment_types:
        power_equipment_summary[equipment_type.plural] = []
        if equipment_type.plural in power_equipment_identifiers:
            for equip in power_equipment_identifiers[equipment_type.plural]:
                # Get the equipment info
                equipment = get_power_equipment(context, equipment_type, equip)
                summary = {
                    "Id": equipment["Info"].dict.get("Id"),
                    "Model": equipment["Info"].dict.get("Model"),
                    "SerialNumber": equipment["Info"].dict.get("SerialNumber"),
                    "State": equipment["Info"].dict.get("Status", {}).get("State"),
                    "Health": equipment["Info"].dict.get("Status", {}).get("Health"),
                }
                power_equipment_summary[equipment_type.plural].append(summary)

    return power_equipment_summary


def print_power_equipment_summary(power_equipment_summary):
    """
    Prints the power equipment summary into a table

    Args:
        power_equipment_summary: The power equipment summary to print
    """

    summary_line_format = "  {:16s} | {:16s} | {:16s} | {:12s} | {:8s}"

    for equipment_type in power_equipment_summary:
        if len(power_equipment_summary[equipment_type]):
            print(equipment_type)
            print(summary_line_format.format("Id", "Model", "Serial Number", "State", "Health"))
            for equipment in power_equipment_summary[equipment_type]:
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


def get_power_equipment(
    context,
    power_equipment_type,
    power_equipment_id=None,
    get_metrics=False,
    get_outlets=False,
    get_mains=False,
    get_branches=False,
    get_feeders=False,
    get_subfeeds=False,
):
    """
    Finds a power equipment matching the given identifier and returns its resource

    Args:
        context: The Redfish client object with an open session
        power_equipment_type: The power equipment type to get; see power_equipment_types enumeration
        power_equipment_id: The power equipment to locate; if None, perform on the only power equipment
        get_metrics: Indicates if the metrics should be returned
        get_outlets: Indicates if the outlets should be returned
        get_mains: Indicates if the mains should be returned
        get_branches: Indicates if the branches should be returned
        get_feeders: Indicates if the feeders should be returned
        get_subfeeds: Indicates if the subfeeds should be returned

    Returns:
        A dictionary containing the power equipment resource and optional subordinate resources
    """

    power_equipment_uri_pattern = "/redfish/v1/PowerEquipment/" + power_equipment_type.plural + "/{}"
    avail_power_equipment = None
    power_equipment = {"Info": None}

    # If given an identifier, get the power equipment directly
    if power_equipment_id is not None:
        power_equipment["Info"] = context.get(power_equipment_uri_pattern.format(power_equipment_id))
    # No identifier given; see if there's exactly one member
    else:
        all_power_equipment = get_power_equipment_ids(context)
        if power_equipment_type.plural not in all_power_equipment:
            raise RedfishPowerEquipmentNotFoundError(
                "The service does not contain any {}".format(power_equipment_type.plural)
            )
        avail_power_equipment = all_power_equipment[power_equipment_type.plural]
        if len(avail_power_equipment) == 1:
            power_equipment["Info"] = context.get(power_equipment_uri_pattern.format(avail_power_equipment[0]))
        else:
            raise RedfishPowerEquipmentNotFoundError(
                "The service contains multiple {}; a target power equipment needs to be specified: {}".format(
                    power_equipment_type.plural, ", ".join(avail_power_equipment)
                )
            )

    # Check the response and return the manager if the response is good
    if power_equipment["Info"].status == 404:
        if avail_power_equipment is None:
            all_equipment = get_power_equipment_ids(context)
            if power_equipment_type.plural not in all_equipment:
                raise RedfishPowerEquipmentNotFoundError(
                    "The service does not contain any {}".format(power_equipment_type.plural)
                )
            avail_equipment = all_equipment[power_equipment_type.plural]
        raise RedfishPowerEquipmentNotFoundError(
            "The service does not contain any {} called {}; valid {}: {}".format(
                power_equipment_type.plural, power_equipment_id, power_equipment_type.plural, ", ".join(avail_equipment)
            )
        )
    verify_response(power_equipment["Info"])

    # Get each of the subordinate resources requested by the caller
    resource_grabber = [
        {"Property": "Metrics", "Parameter": get_metrics, "Collection": False},
        {"Property": "Outlets", "Parameter": get_outlets, "Collection": True},
        {"Property": "Mains", "Parameter": get_mains, "Collection": True},
        {"Property": "Branches", "Parameter": get_branches, "Collection": True},
        {"Property": "Feeders", "Parameter": get_feeders, "Collection": True},
        {"Property": "Subfeeds", "Parameter": get_subfeeds, "Collection": True},
    ]
    for resource in resource_grabber:
        power_equipment[resource["Property"]] = None
        if resource["Parameter"] and resource["Property"] in power_equipment["Info"].dict:
            if resource["Collection"]:
                power_equipment[resource["Property"]] = []
                collection = get_collection_ids(
                    context, power_equipment["Info"].dict[resource["Property"]]["@odata.id"]
                )
                for member_id in collection:
                    member = context.get(
                        power_equipment["Info"].dict[resource["Property"]]["@odata.id"] + "/" + member_id
                    )
                    verify_response(member)
                    power_equipment[resource["Property"]].append(member)
            else:
                power_equipment[resource["Property"]] = context.get(
                    power_equipment["Info"].dict[resource["Property"]]["@odata.id"]
                )
                verify_response(power_equipment[resource["Property"]])

    return power_equipment


def print_power_equipment(power_equipment):
    """
    Prints the power equipment info

    Args:
        power_equipment: The power equipment info to print
    """

    power_equipment_line_format = "  {}: {}"
    print("{} {} Info".format(power_equipment["Info"].dict["EquipmentType"], power_equipment["Info"].dict["Id"]))

    print("")
    power_equipment_properties = [
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
    ]
    for property in power_equipment_properties:
        if property in power_equipment["Info"].dict:
            prop_val = power_equipment["Info"].dict[property]
            if isinstance(prop_val, list):
                prop_val = ", ".join([i for i in prop_val if i is not None])
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format(prop_val.get("State", "N/A"), prop_val.get("Health", "N/A"))
            print(power_equipment_line_format.format(property, prop_val))
    if power_equipment["Metrics"]:
        power_equipment_properties = [
            ("PowerWatts", "Power", "W"),
            ("EnergykWh", "Energy", "kWh"),
            ("TemperatureCelsius", "Temperature", "C"),
            ("HumidityPercent", "Humidity", "%"),
            ("PowerLoadPercent", "PowerLoad", "%"),
            ("AbsoluteHumidity", "AbsoluteHumidity", "g/m^3"),
        ]
        for property in power_equipment_properties:
            if property[0] in power_equipment["Metrics"].dict:
                if power_equipment["Metrics"].dict[property[0]]["Reading"] is None:
                    prop_val = "Unavailable"
                else:
                    prop_val = str(power_equipment["Metrics"].dict[property[0]]["Reading"]) + " " + property[2]
                print(power_equipment_line_format.format(property[1], prop_val))
    print("")


def get_power_equipment_electrical(
    context, power_equipment_type, power_equipment_electrical_type, power_equipment_id=None, electrical_id=None
):
    """
    Finds an outlet or circuit for an instance of power equipment and returns its resource

    Args:
        context: The Redfish client object with an open session
        power_equipment_type: The power equipment type to get; see power_equipment_types enumeration
        power_equipment_electrical_type: The electrical type to get; see power_equipment_electrical_types enumeration
        power_equipment_id: The power equipment to locate; if None, perform on the only power equipment
        electrical_id: The outlet or circuit to locate; if None, perform on the only outlet or circuit

    Returns:
        The outlet or circuit resource
    """

    # Get the power equipment
    power_equipment = get_power_equipment(context, power_equipment_type, power_equipment_id)

    # Check that the power equipment has the desired electrical component type
    if power_equipment_electrical_type.plural not in power_equipment["Info"].dict:
        raise RedfishPowerEquipmentElectricalNotFoundError(
            "{} {} does not contain any {}".format(
                power_equipment_type.plural, power_equipment["Info"].dict["Id"], power_equipment_electrical_type.plural
            )
        )

    power_equipment_electrical_uri_pattern = (
        power_equipment["Info"].dict[power_equipment_electrical_type.plural]["@odata.id"] + "/{}"
    )
    avail_electrical = None

    # If given an identifier, get the outlet or circuit directly
    if electrical_id is not None:
        electrical = context.get(power_equipment_electrical_uri_pattern.format(electrical_id))
    # No identifier given; see if there's exactly one member
    else:
        avail_electrical = get_collection_ids(
            context, power_equipment["Info"].dict[power_equipment_electrical_type.plural]["@odata.id"]
        )
        if len(avail_electrical) == 1:
            electrical = context.get(power_equipment_electrical_uri_pattern.format(avail_electrical[0]))
        else:
            raise RedfishPowerEquipmentElectricalNotFoundError(
                "{} {} contains multiple {}; a target component needs to be specified: {}".format(
                    power_equipment_type.plural,
                    power_equipment["Info"].dict["Id"],
                    power_equipment_electrical_type.plural,
                    ", ".join(avail_electrical),
                )
            )

    # Check the response and return the manager if the response is good
    if electrical.status == 404:
        if avail_electrical is None:
            avail_electrical = get_collection_ids(
                context, power_equipment["Info"].dict[power_equipment_electrical_type.plural]["@odata.id"]
            )
        raise RedfishPowerEquipmentNotFoundError(
            "{} {} does not contain any {} called {}; valid {}: {}".format(
                power_equipment_type.plural,
                power_equipment["Info"].dict["Id"],
                power_equipment_electrical_type.plural,
                electrical_id,
                power_equipment_electrical_type.plural,
                ", ".join(avail_electrical),
            )
        )
    verify_response(electrical)
    return electrical


def print_power_equipment_electrical(electrical):
    """
    Prints the outlet or circuit info

    Args:
        electrical: The outlet or circuit to print
    """

    electrical_line_format = "  {}: {}"
    poly_phase_line_format = "    {:5s}: {}"
    if "#Outlet." in electrical.dict["@odata.type"]:
        print("Outlet {} Info".format(electrical.dict["Id"]))
    else:
        print("{} {} Info".format(electrical.dict["CircuitType"], electrical.dict["Id"]))

    print("")
    # Display the simple properties
    electrical_properties = [
        "Status",
        "CircuitType",
        "CriticalCircuit",
        "ElectricalContext",
        "PhaseWiringType",
        "VoltageType",
        "OutletType",
        "PlugType",
        "NominalVoltage",
        "RatedCurrentAmps",
        "BreakerState",
        "PowerState",
    ]
    for property in electrical_properties:
        if property in electrical.dict:
            prop_val = electrical.dict[property]
            if isinstance(prop_val, list):
                prop_val = ", ".join([i for i in prop_val if i is not None])
            elif property == "PhaseWiringType":
                prop_val = str(phase_wiring_type_strings.get(prop_val, prop_val))
            elif property == "NominalVoltage":
                prop_val = str(voltage_type_strings.get(prop_val, prop_val))
            elif property == "OutletType":
                prop_val = str(receptical_type_strings.get(prop_val, prop_val))
            elif property == "PlugType":
                prop_val = str(plug_type_strings.get(prop_val, prop_val))
            elif property == "Status":
                prop_val = "State: {}, Health: {}".format(prop_val.get("State", "N/A"), prop_val.get("Health", "N/A"))
            else:
                prop_val = str(prop_val)
            print(electrical_line_format.format(property, prop_val))
    # Display the embedded metrics
    electrical_properties = [
        ("Voltage", "Voltage", "V"),
        ("CurrentAmps", "Current", "A"),
        ("PowerWatts", "Power", "W"),
        ("EnergykWh", "Energy", "kWh"),
        ("FrequencyHz", "Frequency", "Hz"),
        ("PowerLoadPercent", "PowerLoad", "%"),
        ("UnbalancedVoltagePercent", "UnbalancedVoltage", "%"),
        ("UnbalancedCurrentPercent", "UnbalancedCurrent", "%"),
    ]
    for property in electrical_properties:
        if property[0] in electrical.dict:
            if electrical.dict[property[0]]["Reading"] is None:
                prop_val = "Unavailable"
            else:
                prop_val = str(electrical.dict[property[0]]["Reading"]) + " " + property[2]
            print(electrical_line_format.format(property[1], prop_val))

        poly_phase_name = "PolyPhase" + property[0]
        if poly_phase_name in electrical.dict:
            if property[0] not in electrical.dict:
                print(electrical_line_format.format(property[1], ""))
            for poly_phase in electrical.dict[poly_phase_name]:
                if electrical.dict[poly_phase_name][poly_phase]["Reading"] is None:
                    prop_val = "Unavailable"
                else:
                    prop_val = (
                        "{:7.2f}".format(electrical.dict["PolyPhase" + property[0]][poly_phase]["Reading"])
                        + " "
                        + property[2]
                    )
                print(poly_phase_line_format.format(line_measurement_strings.get(poly_phase, poly_phase), prop_val))
    print("")


def print_power_equipment_electrical_summary(power_equipment, electrical_type, print_heading):
    """
    Prints the circuit/outlet summary for an instance of power equipment

    Args:
        power_equipment: The power equipment info to print
        electrical_type: The type of electrical info to print
        print_heading: Indicates if the tabling heading should be printed
    """

    if not power_equipment[electrical_type.plural]:
        if print_heading:
            print(
                "{} {} does not contain any {}".format(
                    power_equipment["Info"].dict["EquipmentType"],
                    power_equipment["Info"].dict["Id"],
                    electrical_type.plural,
                )
            )
        return

    electrical_line_format = "  {:16s} | {:18s} | {:20s} | {:12s} | {:12s} | {:12s} | {:12s}"
    if print_heading:
        print(
            "{} {} {}".format(
                power_equipment["Info"].dict["EquipmentType"],
                power_equipment["Info"].dict["Id"],
                electrical_type.plural,
            )
        )
        print("")
    print(
        electrical_line_format.format(
            electrical_type.value + " Id",
            "Nominal Voltage",
            "Phase Wiring",
            "State",
            "Voltage (V)",
            "Current (A)",
            "Power (W)",
        )
    )
    for item in power_equipment[electrical_type.plural]:
        if "PolyPhaseVoltage" in item.dict:
            voltage = "Polyphase"
        else:
            voltage = str(item.dict.get("Voltage", {}).get("Reading", "---"))
        if "PolyPhaseCurrentAmps" in item.dict:
            current = "Polyphase"
        else:
            current = str(item.dict.get("CurrentAmps", {}).get("Reading", "---"))
        voltage_type = item.dict.get("NominalVoltage", "---")
        voltage_type = voltage_type_strings.get(voltage_type, voltage_type)
        phase_wiring_type = item.dict.get("PhaseWiringType", "---")
        phase_wiring_type = phase_wiring_type_strings.get(phase_wiring_type, phase_wiring_type)
        state = str(item.dict.get("Status", {}).get("State", "---"))
        power = str(item.dict.get("PowerWatts", {}).get("Reading", "---"))
        print(
            electrical_line_format.format(
                item.dict["Id"], voltage_type, phase_wiring_type, state, voltage, current, power
            )
        )
    print("")
