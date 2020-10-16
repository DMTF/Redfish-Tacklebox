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

import xlsxwriter

def get_system_inventory( context ):
    """
    Walks a Redfish service for system component information, such as drives,
    processors, and memory

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all system component information
    """

    inventory_list = []

    # Get the Service Root to find the Chassis Collection
    service_root = context.get( "/redfish/v1/" )
    if "Chassis" not in service_root.dict:
        # No Chassis Collection
        return inventory_list

    # Get the Chassis Collection and iterate through its collection
    chassis_col = context.get( service_root.dict["Chassis"]["@odata.id"] )
    for chassis_member in chassis_col.dict["Members"]:
        chassis = context.get( chassis_member["@odata.id"] )

        # Catalog Chassis itself
        chassis_instance = {
            "ChassisName": chassis.dict["Id"],
            "Chassis": [],
            "Processors": [],
            "Memory": [],
            "Drives": [],
            "PCIeDevices": [],
            "StorageControllers": [],
            "NetworkAdapters": []
        }
        inventory_list.append( chassis_instance )
        catalog_resource( chassis.dict, chassis_instance["Chassis"] )

        # Catalog all Drives, PCIeDevices, NetworkAdapters, Systems, and ResourceBlocks in the Chassis
        if "Links" in chassis.dict:
            catalog_array( context, chassis.dict["Links"], "Drives", chassis_instance["Drives"] )
            catalog_array( context, chassis.dict["Links"], "PCIeDevices", chassis_instance["PCIeDevices"] )
            catalog_systems( context, chassis.dict["Links"], "ComputerSystems", chassis_instance )
        catalog_collection( context, chassis.dict, "NetworkAdapters", chassis_instance["NetworkAdapters"] )

    return inventory_list

def catalog_array( context, resource, name, inventory ):
    """
    Catalogs an array of resources for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the array
        name: The name of the property of the array
        inventory: The inventory list to update
    """

    if name in resource:
        for member in resource[name]:
            member_res = context.get( member["@odata.id"] )
            catalog_resource( member_res.dict, inventory )

def catalog_collection( context, resource, name, inventory ):
    """
    Catalogs a collection of resources for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the collection
        name: The name of the property of the collection
        inventory: The inventory list to update
    """

    if name in resource:
        collection = context.get( resource[name]["@odata.id"] )
        for member in collection.dict["Members"]:
            member_res = context.get( member["@odata.id"] )
            catalog_resource( member_res.dict, inventory )

def catalog_systems( context, resource, name, inventory ):
    """
    Catalogs an array of systems for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the array of computer systems
        name: The name of the property of the array
        inventory: The inventory list to update
    """

    if name in resource:
        for system in resource[name]:
            system_res = context.get( system["@odata.id"] )

            # Catalog all Processors, Memory, and PCIeDevices in the System
            catalog_collection( context, system_res.dict, "Processors", inventory["Processors"] )
            catalog_collection( context, system_res.dict, "Memory", inventory["Memory"] )
            catalog_array( context, system_res.dict, "PCIeDevices", inventory["PCIeDevices"] )
            catalog_simple_storage( context, system_res.dict, "SimpleStorage", inventory["Drives"] )
            catalog_storage( context, system_res.dict, "Storage", inventory )

def catalog_simple_storage( context, resource, name, inventory ):
    """
    Catalogs a collection of Simple Storage resources for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the collection
        name: The name of the property of the collection
        inventory: The inventory list to update
    """

    if name in resource:
        collection = context.get( resource[name]["@odata.id"] )
        for member in collection.dict["Members"]:
            member_res = context.get( member["@odata.id"] )
            if "Devices" in member_res.dict:
                for index, drive in enumerate( member_res.dict["Devices"] ):
                    drive["@odata.id"] = "{}#/Devices/{}".format( member_res.dict["@odata.id"], index )
                    drive["@odata.type"] = "#Drive.Drive"
                    drive["Id"] = drive["Name"]
                    catalog_resource( drive, inventory )

def catalog_storage( context, resource, name, inventory ):
    """
    Catalogs a collection of Storage resources for the inventory list

    Args:
        context: The Redfish client object with an open session
        resource: The resource with the collection
        name: The name of the property of the collection
        inventory: The inventory list to update
    """

    if name in resource:
        collection = context.get( resource[name]["@odata.id"] )
        for member in collection.dict["Members"]:
            member_res = context.get( member["@odata.id"] )
            catalog_array( context, member_res.dict, "Drives", inventory["Drives"] )
            if "StorageControllers" in member_res.dict:
                for index, controller in enumerate( member_res.dict["StorageControllers"] ):
                    controller["@odata.type"] = "#StorageController.StorageController"
                    controller["Id"] = controller["MemberId"]
                    catalog_resource( controller, inventory["StorageControllers"] )

def catalog_resource( resource, inventory ):
    """
    Catalogs a resource for the inventory list

    Args:
        resource: The resource to catalog
        inventory: The inventory list to update
    """

    # Scan the inventory to ensure this is a new entry
    for item in inventory:
        if item["Uri"] == resource["@odata.id"]:
            return

    resource_type = resource["@odata.type"].rsplit( "." )[-1]

    location_prop = "Location"
    if resource_type == "Drive":
        location_prop = "PhysicalLocation"

    catalog = {
        "Uri": resource["@odata.id"],
        "PartNumber": resource.get( "PartNumber", None ),
        "SerialNumber": resource.get( "SerialNumber", None ),
        "Manufacturer": resource.get( "Manufacturer", None ),
        "Model": resource.get( "Model", None ),
        "SKU": resource.get( "SKU", None ),
        "AssetTag": resource.get( "AssetTag", None ),
        "Label": resource.get( location_prop, {} ).get( "PartLocation", {} ).get( "ServiceLabel", None ),
        "State": resource.get( "Status", {} ).get( "State", None ),
        "Description": None
    }

    # If no label was found, build a default name
    if catalog["Label"] is None:
        catalog["Label"] = resource_type + ": " + resource["Id"]

    # Build a string description of the component based on other properties
    prop_list = []
    if resource_type == "Chassis":
        prop_list = [ "Model" ]
    elif resource_type == "Processor":
        if catalog["Model"] is not None:
            prop_list = [ "Model" ]
        else:
            prop_list = [ "Manufacturer", "ProcessorArchitecture", "ProcessorType", "TotalCores", "MaxSpeedMHz" ]
    elif resource_type == "Memory":
        prop_list = [ "Manufacturer", "CapacityMiB", "MemoryDeviceType", "MemoryType" ]
    elif resource_type == "Drive":
        prop_list = [ "Manufacturer", "CapacityBytes", "Protocol", "MediaType" ]
    elif resource_type == "PCIeDevice":
        prop_list = [ "Manufacturer", "Model", "DeviceType", "PCIeInterface" ]
    elif resource_type == "StorageController":
        prop_list = [ "Manufacturer", "SpeedGbps", "SupportedDeviceProtocols" ]
    elif resource_type == "NetworkAdapter":
        prop_list = [ "Manufacturer", "Model" ]

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

    inventory.append( catalog )

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
        type_list = [ "Chassis", "Processors", "Memory", "Drives", "PCIeDevices", "StorageControllers", "NetworkAdapters" ]
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
        type_list = [ "Chassis", "Processors", "Memory", "Drives", "PCIeDevices", "StorageControllers", "NetworkAdapters" ]
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
