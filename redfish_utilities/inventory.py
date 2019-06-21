"""
Sensors Module

File : inventory.py

Brief : This file contains the definitions and functionalities for scanning a
        Redfish service for an inventory of components
"""

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
    service_root = context.get( "/redfish/v1/", None )
    if "Chassis" not in service_root.dict:
        # No Chassis Collection
        return inventory_list

    # Get the Chassis Collection and iterate through its collection
    chassis_col = context.get( service_root.dict["Chassis"]["@odata.id"], None )
    for chassis_member in chassis_col.dict["Members"]:
        chassis = context.get( chassis_member["@odata.id"], None )

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
            member_res = context.get( member["@odata.id"], None )
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
        collection = context.get( resource[name]["@odata.id"], None )
        for member in collection.dict["Members"]:
            member_res = context.get( member["@odata.id"], None )
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
            system_res = context.get( system["@odata.id"], None )

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
        collection = context.get( resource[name]["@odata.id"], None )
        for member in collection.dict["Members"]:
            member_res = context.get( member["@odata.id"], None )
            if "Devices" in member_res.dict:
                for index, drive in enumerate( member_res.dict["Devices"] ):
                    drive["@odata.id"] = "{}#/Devices/{}".format( member_res.dict["@odata.id"], index )
                    drive["@odata.type"] = "#SimpleStorage.SimpleStorage"
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
        collection = context.get( resource[name]["@odata.id"], None )
        for member in collection.dict["Members"]:
            member_res = context.get( member["@odata.id"], None )
            catalog_array( context, member_res.dict, "Drives", inventory["Drives"] )
            if "StorageControllers" in member_res.dict:
                for index, controller in enumerate( member_res.dict["StorageControllers"] ):
                    controller["@odata.type"] = "#StorageController.StorageController"
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
        "State": resource.get( "Status", {} ).get( "State", None )
    }

    # If no label was found, build a default name
    if catalog["Label"] is None:
        catalog["Label"] = resource["Id"]

    inventory.append( catalog )

def print_system_inventory( inventory_list ):
    """
    Prints the system inventory list into a table

    Args:
        inventory_list: The inventory list to print
    """

    inventory_line_format = "  {:30s} | {:40s} | {:20} | {:20s}"
    inventory_line_format_empty = "  {:30s} | Not Present"

    # Go through each chassis instance
    for chassis in inventory_list:
        print( "'" + chassis["ChassisName"] + "' Inventory" )
        print( inventory_line_format.format( "Name", "Model", "Part Number", "Serial Number" ) )

        # Go through each component type in the chassis
        type_list = [ "Chassis", "Processors", "Memory", "Drives", "PCIeDevices", "StorageControllers", "NetworkAdapters" ]
        for inv_type in type_list:
            # Go through each component and prints its info
            for item in chassis[inv_type]:
                model = item["Model"]
                if model is None:
                    model = "N/A"
                part_num = item["PartNumber"]
                if part_num is None:
                    part_num = "N/A"
                serial_num = item["SerialNumber"]
                if serial_num is None:
                    serial_num = "N/A"

                if item["State"] == "Absent":
                    print( inventory_line_format_empty.format( item["Label"][:30] ) )
                else:
                    print( inventory_line_format.format( item["Label"][:30], model[:40], part_num[:20], serial_num[:20] ) )
        print( "" )
