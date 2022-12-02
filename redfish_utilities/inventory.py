#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Inventory Module

File : inventory.py

Brief : This file contains the definitions and functionalities for scanning a
        Redfish service for an inventory of components
"""

import warnings
import xlsxwriter
from .messages import verify_response
from . import config

class RedfishChassisNotFoundError( Exception ):
    """
    Raised when a matching chassis cannot be found
    """
    pass

def get_system_inventory( context ):
    """
    Walks a Redfish service for system component information, such as drives,
    processors, and memory

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all system component information
    """

    chassis_uri_pattern = "/redfish/v1/Chassis/{}"
    inventory_list = []

    # Get the set of chassis instances to initialize the structure
    try:
        chassis_ids = get_chassis_ids( context )
    except:
        # No chassis instances
        return inventory_list

    # Set up the inventory list based on the chassis instances found
    # This is done prior to cataloging anything since depending on how links are used, some devices might point back to a chassis instance not yet cataloged
    for chassis_id in chassis_ids:
        chassis_instance = {
            "ChassisName": chassis_id,
            "Chassis": [],
            "Processors": [],
            "Memory": [],
            "Drives": [],
            "PCIeDevices": [],
            "StorageControllers": [],
            "NetworkAdapters": [],
            "Switches": []
        }
        inventory_list.append( chassis_instance )

    # Go through each chassis and catalog the results
    for chassis_id in chassis_ids:
        chassis_uri = chassis_uri_pattern.format( chassis_id )
        chassis = context.get( chassis_uri )
        try:
            verify_response( chassis )
        except:
            if config.__workarounds__:
                warnings.warn( "Could not access '{}'.  Contact your vendor.  Skipping...".format( chassis_uri ) )
                continue
            else:
                raise
        catalog_resource( context, chassis.dict, inventory_list, chassis_id )

    return inventory_list

def catalog_array( context, resource, name, inventory, chassis_id ):
    """
    Catalogs an array of resources for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the array
        name: The name of the property of the array
        inventory: The inventory to update
        chassis_id: The identifier for the chassis being scanned
    """

    if name in resource:
        for member in resource[name]:
            member_res = context.get( member["@odata.id"] )
            try:
                verify_response( member_res )
            except:
                if config.__workarounds__:
                    warnings.warn( "Could not access '{}'.  Contact your vendor.  Skipping...".format( member["@odata.id"] ) )
                    continue
                else:
                    raise
            catalog_resource( context, member_res.dict, inventory, chassis_id )

def catalog_collection( context, resource, name, inventory, chassis_id ):
    """
    Catalogs a collection of resources for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the array
        name: The name of the property of the collection
        inventory: The inventory to update
        chassis_id: The identifier for the chassis being scanned
    """

    if name in resource:
        collection = context.get( resource[name]["@odata.id"] )
        try:
            verify_response( collection )
        except:
            if config.__workarounds__:
                warnings.warn( "Could not access '{}'.  Contact your vendor.  Skipping...".format( resource[name]["@odata.id"] ) )
                return
            else:
                raise
        catalog_array( context, collection.dict, "Members", inventory, chassis_id )

def catalog_resource( context, resource, inventory, chassis_id ):
    """
    Catalogs a resource for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource to catalog
        inventory: The inventory to update
        chassis_id: The identifier for the chassis being scanned
    """

    resource_type = resource["@odata.type"].rsplit(".")[-1]

    # Based on the resource type, see if anything needs to be cataloged within it
    if resource_type == "Chassis":
        # Catalog all of the components within the chassis
        catalog_collection( context, resource, "NetworkAdapters", inventory, chassis_id )
        catalog_collection( context, resource, "Drives", inventory, chassis_id )
        catalog_collection( context, resource, "PCIeDevices", inventory, chassis_id )
        catalog_collection( context, resource, "Memory", inventory, chassis_id )
        if "Links" in resource:
            catalog_array( context, resource["Links"], "Drives", inventory, chassis_id )
            catalog_array( context, resource["Links"], "PCIeDevices", inventory, chassis_id )
            catalog_array( context, resource["Links"], "Switches", inventory, chassis_id )
            catalog_array( context, resource["Links"], "ComputerSystems", inventory, chassis_id )
    elif resource_type == "ComputerSystem":
        # Catalog all of the components within the system
        catalog_collection( context, resource, "Processors", inventory, chassis_id )
        catalog_collection( context, resource, "Memory", inventory, chassis_id )
        catalog_collection( context, resource, "SimpleStorage", inventory, chassis_id )
        catalog_collection( context, resource, "Storage", inventory, chassis_id )
        # The system itself does not get cataloged (the chassis representation should cover this)
        return
    elif resource_type == "Storage":
        # Catalog the drives and storage controllers in the storage subsystem
        catalog_array( context, resource, "Drives", inventory, chassis_id )
        if "StorageControllers" in resource:
            for index, controller in enumerate( resource["StorageControllers"] ):
                controller["@odata.type"] = "#StorageController.StorageController"
                controller["Id"] = controller["MemberId"]
                catalog_resource( context, controller, inventory, chassis_id )
        # The storage subsystem itself does not get cataloged
        return
    elif resource_type == "SimpleStorage":
        # If there is a full storage representation of this resource, skip it
        if "Links" in resource:
            if "Storage" in resource["Links"]:
                return

        # Catalog the devices (as drives)
        if "Devices" in resource:
            for index, drive in enumerate( resource["Devices"] ):
                drive["@odata.id"] = "{}#/Devices/{}".format( resource["@odata.id"], index )
                drive["@odata.type"] = "#Drive.Drive"
                drive["Id"] = drive["Name"]
                catalog_resource( context, drive, inventory, chassis_id )
        # The simple storage subsystem itself does not get cataloged
        return

    # If the resource has a pointer back to chassis, use the identifier in the link for cataloging
    if "Links" in resource:
        if "Chassis" in resource["Links"]:
            if isinstance( resource["Links"]["Chassis"], dict ):
                chassis_id = resource["Links"]["Chassis"]["@odata.id"].strip( "/" ).split( "/" )[-1]

    # Determine the location property
    location_prop = "Location"
    if resource_type == "Drive":
        location_prop = "PhysicalLocation"

    # Pull out all relevant properties for the catalog
    catalog = {
        "Uri": resource["@odata.id"],
        "PartNumber": resource.get( "PartNumber", None ),
        "SerialNumber": resource.get( "SerialNumber", None ),
        "Manufacturer": resource.get( "Manufacturer", None ),
        "Model": resource.get( "Model", None ),
        "SKU": resource.get( "SKU", None ),
        "AssetTag": resource.get( "AssetTag", None ),
        "Label": None,
        "State": None,
        "Description": None
    }
    # For nested properties, need to protect against malformed payloads to avoid exceptions
    try:
        catalog["Label"] = resource.get( location_prop, {} ).get( "PartLocation", {} ).get( "ServiceLabel", None )
    except:
        pass
    try:
        catalog["State"] = resource.get( "Status", {} ).get( "State", None )
    except:
        pass
    # Ensure all fields are strings
    for item in catalog:
        if not isinstance( catalog[item], str ):
            catalog[item] = None

    # If no label was found, build a default name
    if catalog["Label"] is None:
        catalog["Label"] = resource_type + ": " + resource["Id"]

    # Build a string description of the component based on other properties
    entry_tag = None
    prop_list = []
    if resource_type == "Chassis":
        entry_tag = "Chassis"
        prop_list = [ "Model" ]
    elif resource_type == "Processor":
        entry_tag = "Processors"
        if catalog["Model"] is not None:
            prop_list = [ "Model" ]
        else:
            prop_list = [ "Manufacturer", "ProcessorArchitecture", "ProcessorType", "TotalCores", "MaxSpeedMHz" ]
    elif resource_type == "Memory":
        entry_tag = "Memory"
        prop_list = [ "Manufacturer", "CapacityMiB", "MemoryDeviceType", "MemoryType" ]
    elif resource_type == "Drive":
        entry_tag = "Drives"
        prop_list = [ "Manufacturer", "CapacityBytes", "Protocol", "MediaType" ]
    elif resource_type == "PCIeDevice":
        entry_tag = "PCIeDevices"
        prop_list = [ "Manufacturer", "Model", "DeviceType", "PCIeInterface" ]
    elif resource_type == "StorageController":
        entry_tag = "StorageControllers"
        prop_list = [ "Manufacturer", "SpeedGbps", "SupportedDeviceProtocols" ]
    elif resource_type == "NetworkAdapter":
        entry_tag = "NetworkAdapters"
        prop_list = [ "Manufacturer", "Model" ]
    elif resource_type == "Switch":
        entry_tag = "Switches"
        prop_list = [ "Manufacturer", "Model" ]
    if entry_tag is None:
        # No handling set up for this resource type
        # Should not happen; check the types against the possible lists
        return

    # Based on the listed properties for the resource type, build the description string
    if catalog["State"] != "Absent":
        description_str = ""
        for prop in prop_list:
            if resource.get( prop, None ) is not None:
                prop_val = resource[prop]
                # Some properties require refinement
                if prop == "TotalCores":
                    prop_val = str( prop_val ) + " Cores"
                elif prop == "MaxSpeedMHz":
                    prop_val = "@ " + str( prop_val ) + "MHz"
                elif prop == "CapacityMiB":
                    prop_val = str( prop_val ) + "MB"
                elif prop == "CapacityBytes":
                    prop_val = str( int( prop_val / ( 2 ** 30 ) ) ) + "GB"
                elif prop == "SpeedGbps":
                    prop_val = str( prop_val ) + "Gbps"
                elif prop == "SupportedDeviceProtocols":
                    prop_val = "/".join( prop_val ) + " Controller"
                elif prop == "DeviceType":
                    prop_val = prop_val + " PCIe Device"
                elif prop == "PCIeInterface":
                    if "MaxPCIeType" in prop_val:
                        prop_val = "@" + " " + prop_val["MaxPCIeType"]
                    else:
                        continue
                description_str = description_str + " " + prop_val
            else:
                # Some properties will have a default if not found
                if prop == "MediaType":
                    description_str = description_str + " Drive"
                elif prop == "SupportedDeviceProtocols":
                    description_str = description_str + " Storage Controller"
        catalog["Description"] = description_str.strip()

    # Find the inventory instance to update based on the chassis identifier
    inventory_instance = None
    for chassis_inventory in inventory:
        if chassis_inventory["ChassisName"] == chassis_id:
            inventory_instance = chassis_inventory
    if inventory_instance is None:
        # No matching spot to put this entry in the inventory
        return
    # Check if this is a new entry
    for item in inventory_instance[entry_tag]:
        if item["Uri"] == resource["@odata.id"]:
            return

    inventory_instance[entry_tag].append( catalog )

def print_system_inventory( inventory_list, details = False, skip_absent = False ):
    """
    Prints the system inventory list into a table

    Args:
        inventory_list: The inventory list to print
        details: True to print all of the detailed info
        skip_absent: True to skip printing absent components
    """

    inventory_line_format = "  {:35s} | {}"
    inventory_line_format_detail = "  {:35s} | {}: {}"
    inventory_line_format_empty = "  {:35s} | Not Present"

    # Go through each chassis instance
    for chassis in inventory_list:
        print( "'" + chassis["ChassisName"] + "' Inventory" )
        print( inventory_line_format.format( "Name", "Description" ) )

        # Go through each component type in the chassis
        type_list = [ "Chassis", "Processors", "Memory", "Drives", "PCIeDevices", "StorageControllers", "NetworkAdapters", "Switches" ]
        for inv_type in type_list:
            # Go through each component and prints its info
            for item in chassis[inv_type]:
                if item["State"] == "Absent":
                    if not skip_absent:
                        print( inventory_line_format_empty.format( item["Label"][:35] ) )
                else:
                    print( inventory_line_format.format( item["Label"][:35], item["Description"] ) )

                    if details:
                        detail_list = [ "Manufacturer", "Model", "SKU", "PartNumber", "SerialNumber", "AssetTag" ]
                        for detail in detail_list:
                            if item[detail] is not None:
                                print( inventory_line_format_detail.format( "", detail, item[detail] ) )
        print( "" )

def write_system_inventory( inventory_list, file_name ):
    """
    Write the system inventory list into a spreadsheet

    Args:
        inventory_list: The inventory list to write to an Excel spreadsheet
        file_name: The name of the file for the spreadsheet
    """

    # Excel workbook to save data extracted and parsed
    workbook = xlsxwriter.Workbook( "./{}.xlsx".format( file_name ) )

    worksheet = workbook.add_worksheet( "Device Inventory" )
    cell_header_format = workbook.add_format( { 'bold': True, 'bg_color': 'yellow' } )
    cell_name_format = workbook.add_format( { 'bold': True } )

    column = 0
    row = 0

    # Adds header to Excel file
    header = [ "NAME", "DESCRIPTION", "MANUFACTURER", "MODEL", "SKU", "PART NUMBER", "SERIAL NUMBER", "ASSET TAG" ]
    for column_title in header:
        worksheet.write( row, column, column_title, cell_header_format )
        column += 1
    row = 1

    for chassis in inventory_list:
        # Go through each component type in the chassis
        type_list = [ "Chassis", "Processors", "Memory", "Drives", "PCIeDevices", "StorageControllers", "NetworkAdapters", "Switches" ]
        for inv_type in type_list:
            # Go through each component and prints its info
            for item in chassis[inv_type]:
                column = 0
                worksheet.write( row, column, inv_type, cell_name_format )
                column += 1
                detail_list = [ "Description", "Manufacturer", "Model", "SKU", "PartNumber", "SerialNumber", "AssetTag" ]
                for detail in detail_list:
                    worksheet.write( row, column, item[detail] )
                    column += 1
                row += 1

    workbook.close()

def get_chassis_ids( context ):
    """
    Finds the chassis collection and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list of identifiers of the members of the chassis collection
    """

    # Get the service root to find the chassis collection
    service_root = context.get( "/redfish/v1/" )
    if "Chassis" not in service_root.dict:
        # No system collection
        raise RedfishChassisNotFoundError( "Service does not contain a chassis collection" )

    # Get the chassis collection and iterate through its collection
    avail_chassis = []
    chassis_col = context.get( service_root.dict["Chassis"]["@odata.id"] )
    while True:
        for chassis_member in chassis_col.dict["Members"]:
            avail_chassis.append( chassis_member["@odata.id"].strip( "/" ).split( "/" )[-1] )
        if "Members@odata.nextLink" not in chassis_col.dict:
            break
        chassis_col = context.get( chassis_col.dict["Members@odata.nextLink"] )
    return avail_chassis
