#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Assembly Module

File : assembly.py

Brief : This file contains the definitions and functionalities for managing
        assemblies on a Redfish service
"""

from .messages import verify_response


class RedfishAssemblyNotFoundError(Exception):
    """
    Raised when an assembly index cannot be found
    """

    pass


class RedfishAssemblyNoBinaryDataError(Exception):
    """
    Raised when an assembly index does not contain binary data
    """

    pass


def get_assembly(context, uri):
    """
    Collects assembly information from a Redfish service

    Args:
        context: The Redfish client object with an open session
        uri: The URI of the assembly to get

    Returns:
        A list containing all assemblies from the URI
    """

    # Get the assembly
    assembly = context.get(uri)
    verify_response(assembly)
    return assembly.dict.get("Assemblies", [])


def print_assembly(assemblies, index=None):
    """
    Prints assembly information into a table

    Args:
        assemblies: An array of assembly information to print
        index: If specified, prints only the desired index
    """

    assembly_format_header = " {:5s} | {} {}"
    assembly_format = " {:5s} | {}: {}"
    assembly_properties = [
        "Model",
        "PartNumber",
        "SparePartNumber",
        "SKU",
        "SerialNumber",
        "Producer",
        "Vendor",
        "ProductionDate",
        "Version",
        "EngineeringChangeLevel",
    ]

    # If an index is specified, isolate to the one index
    if index is not None:
        if index < 0 or index >= len(assemblies):
            raise RedfishAssemblyNotFoundError(
                "Assembly contains {} entries; index {} is not valid".format(len(assemblies), index)
            )
        assemblies = [assemblies[index]]

    # Go through each assembly
    for assembly in assemblies:
        # Print the heading
        heading_details = []
        state = assembly.get("Status", {}).get("State")
        if state:
            heading_details.append(state)
        health = assembly.get("Status", {}).get("Health")
        if health:
            heading_details.append(health)
        heading_details = ", ".join(heading_details)
        if len(heading_details) != 0:
            heading_details = "(" + heading_details + ")"
        print(assembly_format_header.format(assembly["MemberId"], assembly["Name"], heading_details))

        # Print any of the found properties
        for property in assembly_properties:
            if property in assembly:
                print(assembly_format.format("", property, assembly[property]))


def download_assembly(context, assemblies, filepath, index=None):
    """
    Downloads the binary data of an assembly to a file

    Args:
        context: The Redfish client object with an open session
        assemblies: An array of assembly information
        filepath: The filepath to download the binary data
        index: The index into the assemblies array to download; if None, perform on index 0 if there's only 1 assembly
    """

    # Get the binary data URI
    binary_data_uri = get_assembly_binary_data_uri(assemblies, index)

    # Download the data and save it
    response = context.get(binary_data_uri)
    verify_response(response)
    with open(filepath, "wb") as binary_file:
        binary_file.write(response.read)


def upload_assembly(context, assemblies, filepath, index=None):
    """
    Uploads the binary data of a file to an assembly

    Args:
        context: The Redfish client object with an open session
        assemblies: An array of assembly information
        filepath: The filepath of the binary data to upload
        index: The index into the assemblies array to upload; if None, perform on index 0 if there's only 1 assembly
    """

    # Get the binary data URI
    binary_data_uri = get_assembly_binary_data_uri(assemblies, index)

    # Upload the binary data
    with open(filepath, "rb") as binary_file:
        data = binary_file.read()
    response = context.put(binary_data_uri, body=data)
    verify_response(response)


def get_assembly_binary_data_uri(assemblies, index=None):
    """
    Locates the binary data URI for a target assembly

    Args:
        assemblies: An array of assembly information
        index: The index into the assemblies array to download; if None, perform on index 0 if there's only 1 assembly

    Returns:
        A string containing the binary data URI
    """

    # If an index is specified, isolate to the one index
    if index is None:
        index = 0
        if len(assemblies) != 1:
            raise RedfishAssemblyNotFoundError(
                "Assembly contains {} entries; an index needs to be specified".format(len(assemblies))
            )
    else:
        if index < 0 or index >= len(assemblies):
            raise RedfishAssemblyNotFoundError(
                "Assembly contains {} entries; index {} is not valid".format(len(assemblies), index)
            )

    # Get the binary data URI
    binary_data_uri = assemblies[index].get("BinaryDataURI")
    if binary_data_uri is None:
        # No binary data
        raise RedfishAssemblyNoBinaryDataError("Assembly index {} does not contain binary data".format(index))
    return binary_data_uri
