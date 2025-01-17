#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Licenses Module

File : licenses.py

Brief : This file contains the definitions and functionalities for managing
        licenses on a Redfish service
"""

import base64
import os
from .collections import get_collection_ids
from .messages import verify_response


class RedfishLicenseServiceNotFoundError(Exception):
    """
    Raised when the license service cannot be found
    """

    pass


class RedfishLicenseCollectionNotFoundError(Exception):
    """
    Raised when the license collection cannot be found
    """

    pass


class RedfishLicenseNotFoundError(Exception):
    """
    Raised when a specific license cannot be found
    """

    pass


class RedfishInstallLicenseNotFoundError(Exception):
    """
    Raised when the license service does not contain the Install action
    """

    pass


def get_licenses(context):
    """
    Collects license information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all licenses
    """

    license_list = []
    license_collection = get_license_collection(context)

    # Get the identifiers of the collection
    license_col = get_collection_ids(context, license_collection)

    # Get each member and add it to the response list
    for license_id in license_col:
        license = context.get(license_collection + "/" + license_id)
        verify_response(license)
        license_list.append(license.dict)

    return license_list


def print_licenses(license_list, details=False):
    """
    Prints the license list into a table

    Args:
        license_list: The license list to print
        details: True to print all the detailed info
    """

    license_format = "  {:30s} | {}"
    license_format_detail = "  {:30s} | {}: {}"
    info_properties = [
        {"Format": "{}", "Property": "EntitlementId"},
        {"Format": "Installed on {}", "Property": "InstallDate"},
        {"Format": "Expires on {}", "Property": "ExpirationDate"},
    ]
    detail_list = [
        "Description",
        "LicenseType",
        "LicenseOrigin",
        "Removable",
        "Manufacturer",
        "SKU",
        "PartNumber",
        "SerialNumber",
        "AuthorizationScope",
        "MaxAuthorizedDevices",
        "RemainingUseCount",
    ]

    print("")
    print(license_format.format("License", "Details"))

    # Go through each license
    for license in license_list:
        info_list = []
        # Build the general info string
        for info in info_properties:
            if info["Property"] in license:
                info_string = info["Format"].format(license[info["Property"]])
            else:
                if info["Property"] == "EntitlementId":
                    # Fallback to ensure there is always something to show
                    info_string = "License " + license["Id"]
            info_list.append(info_string)

        # Print the license info
        print(license_format.format(license["Id"], ", ".join(info_list)))

        # Print details if requested
        if details:
            for detail in detail_list:
                if detail in license:
                    print(license_format_detail.format("", detail, license[detail]))

    print("")


def install_license(context, license_path):
    """
    Installs a new license

    Args:
        context: The Redfish client object with an open session
        license_path: The filepath or URI of the license to install

    Returns:
        The response of the operation
    """

    # Get the license service
    license_service = get_license_service(context)

    # Determine which installation method to use based on the provided license path
    if os.path.isfile(license_path):
        # Local file; perform via a POST to the license collection
        if "Licenses" not in license_service:
            raise RedfishLicenseCollectionNotFoundError("The license service does not contain a license collection")
        install_uri = license_service["Licenses"]["@odata.id"]

        # Read in the file and convert it to a Base64-encoded string
        with open(license_path, "rb") as file:
            license_file = file.read()
        payload = {"LicenseString": base64.b64encode(license_file).decode("utf-8")}
    else:
        # Remote file; perform via a POST to the Install action
        if "Actions" not in license_service:
            raise RedfishInstallLicenseNotFoundError("The license service does not contain actions")
        if "#LicenseService.Install" not in license_service["Actions"]:
            raise RedfishInstallLicenseNotFoundError("The license service does not contain the Install action")
        install_uri = license_service["Actions"]["#LicenseService.Install"]["target"]

        payload = {"LicenseFileURI": license_path}

    # Install the license
    response = context.post(install_uri, body=payload)
    verify_response(response)
    return response


def delete_license(context, license_id):
    """
    Deletes a license

    Args:
        context: The Redfish client object with an open session
        license_id: The identifier of the license to delete

    Returns:
        The response of the operation
    """

    # Get the identifiers of the collection
    license_collection = get_license_collection(context)
    avail_licenses = get_collection_ids(context, license_collection)
    if license_id not in avail_licenses:
        raise RedfishLicenseNotFoundError(
            "License service does not contain the license '{}'; available licenses: {}".format(
                license_id, ", ".join(avail_licenses)
            )
        )

    # Delete the requested license
    response = context.delete(license_collection + "/" + license_id)
    verify_response(response)
    return response


def get_license_service(context):
    """
    Collects the license service information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        An object containing information about the license service
    """

    # Get the service root to find the license service
    service_root = context.get("/redfish/v1/")
    if "LicenseService" not in service_root.dict:
        # No event service
        raise RedfishLicenseServiceNotFoundError("Service does not contain a license service")

    # Get the license service
    license_service = context.get(service_root.dict["LicenseService"]["@odata.id"])
    verify_response(license_service)
    return license_service.dict


def get_license_collection(context):
    """
    Finds the license collection for the Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        The URI for the license collection
    """

    # Get the license service to find the license collection
    license_service = get_license_service(context)
    if "Licenses" not in license_service:
        # No license collection
        raise RedfishLicenseCollectionNotFoundError("Service does not contain a license collection")

    return license_service["Licenses"]["@odata.id"]
