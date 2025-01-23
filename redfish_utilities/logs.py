#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Logs Module

File : logs.py

Brief : This file contains the definitions and functionalities for interacting
        with the log service for a given Redfish service
"""

from .collections import get_collection_ids
from .messages import verify_response
from enum import Enum


class RedfishLogServiceNotFoundError(Exception):
    """
    Raised when a matching log service cannot be found
    """

    pass


class RedfishClearLogNotFoundError(Exception):
    """
    Raised when a log service does not contain the clear log action
    """

    pass


class RedfishCollectDiagnosticDataNotFoundError(Exception):
    """
    Raised when a log service does not contain the collect diagnostic data action
    """

    pass


class RedfishDiagnosticDataNotFoundError(Exception):
    """
    Raised when the requested diagnostic data cannot be found
    """

    pass


class log_container(Enum):
    """
    Types of resources that contain log services
    """

    MANAGER = "Managers"
    CHASSIS = "Chassis"
    SYSTEM = "Systems"


class diagnostic_data_types(Enum):
    """
    Types of diagnostic data that can be requested
    """

    MANAGER = "Manager"
    PRE_OS = "PreOS"
    OS = "OS"
    OEM = "OEM"

    def __str__(self):
        return self.value


def get_log_service_ids(context, container_type=log_container.MANAGER, container_id=None):
    """
    Finds the log service collection and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session
        container_type: The type of resource containing the log service (manager, system, or chassis)
        container_id: The container instance to locate; if None, perform on the only container

    Returns:
        The container identifier that was located
        A list of identifiers of the members of the log service collection
    """

    # Get the Service Root to find the resource collection
    service_root = context.get("/redfish/v1/")
    if container_type.value not in service_root.dict:
        # No resource collection
        raise RedfishLogServiceNotFoundError("Service does not contain a {} collection".format(container_type.value))

    # Get the resource collection and iterate through its collection to find the matching container instance
    avail_containers = get_collection_ids(context, service_root.dict[container_type.value]["@odata.id"])
    if container_id is None:
        if len(avail_containers) == 1:
            container_id = avail_containers[0]
        else:
            raise RedfishLogServiceNotFoundError(
                "Service does not contain exactly one resource in {}; a target container needs to be specified: {}".format(
                    container_type.value, ", ".join(avail_containers)
                )
            )
    else:
        if container_id not in avail_containers:
            raise RedfishLogServiceNotFoundError(
                "Service does not contain a resource in {} called {}; valid resources: {}".format(
                    container_type.value, container_id, ", ".join(avail_containers)
                )
            )

    # Get the container and check that it has log services
    container = context.get(service_root.dict[container_type.value]["@odata.id"] + "/" + container_id)
    if "LogServices" not in container.dict:
        raise RedfishLogServiceNotFoundError("Container {} does not contain a log services collection".format(container_id))

    # Get the log service collection and iterate through its collection
    return container_id, get_collection_ids(context, container.dict["LogServices"]["@odata.id"])

def get_log_service(context, container_type=log_container.MANAGER, container_id=None, log_service_id=None):
    """
    Finds a log service matching the given ID and returns its resource

    Args:
        context: The Redfish client object with an open session
        container_type: The type of resource containing the log service (manager, system, or chassis)
        container_id: The container instance to locate; if None, perform on the only container
        log_service_id: The log service to locate; if None, perform on the only log service

    Returns:
        The log service resource
    """

    # Get the log service collection and find a matching member
    container_id, avail_logs = get_log_service_ids(context, container_type, container_id)
    if log_service_id is None:
        if len(avail_logs) == 1:
            log_service_id = avail_logs[0]
        else:
            raise RedfishLogServiceNotFoundError(
                "{} does not contain exactly one log service; a target log service needs to be specified: {}".format(
                    container_id, ", ".join(avail_logs)
                )
            )
    else:
        if log_service_id not in avail_logs:
            raise RedfishLogServiceNotFoundError(
                "{} does not contain a log service called {}; valid log services: {}".format(
                    container_id, log_service_id, ", ".join(avail_logs)
                )
            )

    # Get the log service
    return context.get("/redfish/v1/" + container_type.value + "/" + container_id + "/LogServices/" + log_service_id)


def get_log_entries(context, container_type=log_container.MANAGER, container_id=None, log_service_id=None):
    """
    Finds the log entries of a log service matching the given ID

    Args:
        context: The Redfish client object with an open session
        container_type: The type of resource containing the log service (manager, system, or chassis)
        container_id: The container instance with the log service; if None, perform on the only container
        log_service_id: The log service with the logs; if None, perform on the only log service

    Returns:
        An array of log entries
    """

    log_service = get_log_service(context, container_type, container_id, log_service_id)

    # Read in the log entries
    log_entries = []
    log_entry_col = context.get(log_service.dict["Entries"]["@odata.id"])
    log_entries.extend(log_entry_col.dict["Members"])

    # If a next link is provided, iterate over it and add to the log entry list
    while "Members@odata.nextLink" in log_entry_col.dict:
        log_entry_col = context.get(log_entry_col.dict["Members@odata.nextLink"])
        log_entries.extend(log_entry_col.dict["Members"])

    return log_entries


def print_log_entries(log_entries, details=False):
    """
    Prints a set of log entries in a table

    Args:
        log_entries: The log entries to print
        details: Flag indicating if details should be displayed
    """

    # Set up templates
    entry_line_format = "  {:5s} | {:25s} | {}"
    detail_line_format = "  {:33s} | {}: {}"
    detail_list = [
        "Severity",
        "EntryType",
        "OemRecordFormat",
        "EntryCode",
        "OemLogEntryCode",
        "SensorType",
        "OemSensorType",
        "GeneratorId",
        "SensorNumber",
        "EventType",
        "EventId",
        "EventGroupId",
        "MessageId",
        "MessageArgs",
    ]
    print(entry_line_format.format("Id", "Timestamp", "Message"))

    # Go through each entry and print the info
    for entry in log_entries:
        timestamp_property = "Created"
        if "EventTimestamp" in entry:
            timestamp_property = "EventTimestamp"
        print(
            entry_line_format.format(
                entry["Id"],
                entry.get(timestamp_property, "Unknown"),
                entry["Message"].replace("\n", "; "),
            )
        )
        if details:
            for detail in detail_list:
                if detail in entry:
                    print(detail_line_format.format("", detail, entry[detail]))


def clear_log_entries(context, container_type=log_container.MANAGER, container_id=None, log_service_id=None):
    """
    Clears the log entries of a log service matching the given ID

    Args:
        context: The Redfish client object with an open session
        container_type: The type of resource containing the log service (manager, system, or chassis)
        container_id: The container instance with the log service; if None, perform on the only container
        log_service_id: The log service with the logs; if None, perform on the only log service

    Returns:
        The response of the action
    """

    log_service = get_log_service(context, container_type, container_id, log_service_id)

    # Find the ClearLog action
    if "Actions" not in log_service.dict:
        raise RedfishClearLogNotFoundError("Log service does not support ClearLog")
    if "#LogService.ClearLog" not in log_service.dict["Actions"]:
        raise RedfishClearLogNotFoundError("Log service does not support ClearLog")
    clear_uri = log_service.dict["Actions"]["#LogService.ClearLog"]["target"]

    # Clear the log
    response = context.post(clear_uri, body={})
    verify_response(response)
    return response


def collect_diagnostic_data(
    context,
    container_type=log_container.MANAGER,
    container_id=None,
    log_service_id=None,
    diagnostic_data_type=None,
    oem_data_type=None,
):
    """
    Performs diagnostic data collection of a log service matching the given ID

    Args:
        context: The Redfish client object with an open session
        container_type: The type of resource containing the log service (manager, system, or chassis)
        container_id: The container instance with the log service; if None, perform on the only container
        log_service_id: The log service with the logs; if None, perform on the only log service
        diagnostic_data_type: The type of diagnostic data to collect (manager, pre OS, OS, OEM)
        oem_data_type: The type of OEM data to collect

    Returns:
        The response of the action
    """

    log_service = get_log_service(context, container_type, container_id, log_service_id)

    # Find the ClearLog action
    if "Actions" not in log_service.dict:
        raise RedfishCollectDiagnosticDataNotFoundError("Log service does not support CollectDiagnosticData")
    if "#LogService.CollectDiagnosticData" not in log_service.dict["Actions"]:
        raise RedfishCollectDiagnosticDataNotFoundError("Log service does not support CollectDiagnosticData")
    collect_uri = log_service.dict["Actions"]["#LogService.CollectDiagnosticData"]["target"]

    # Collect diagnostic data
    if diagnostic_data_type is None:
        diagnostic_data_type = diagnostic_data_types.MANAGER
    payload = {"DiagnosticDataType": diagnostic_data_type.value}
    if oem_data_type is not None and diagnostic_data_type == diagnostic_data_types.OEM:
        # Only include OEMDiagnosticDataType if the OEM type is requested
        payload["OEMDiagnosticDataType"] = oem_data_type
    response = context.post(collect_uri, body=payload)
    verify_response(response)
    return response


def download_diagnostic_data(context, collect_response):
    """
    Downloads the diagnostic data based on the response from the collect action

    Args:
        context: The Redfish client object with an open session
        collect_response: The response object from the collect diagnostic data action

    Returns:
        The name of the file downloaded from the service
        An array of bytes containing the file contents
    """

    # Follow the Location header to the log entry
    entry_uri = collect_response.getheader("Location")
    if entry_uri is None:
        raise RedfishDiagnosticDataNotFoundError(
            "The response to collecting diagnostic data does not contain a location for the data"
        )

    # Get the log entry
    response = context.get(entry_uri)
    if "AdditionalDataURI" not in response.dict:
        raise RedfishDiagnosticDataNotFoundError(
            "The log entry for the collected data does not contain an additional data link"
        )

    # Download the file
    filename = response.dict["AdditionalDataURI"].split("/")[-1]
    response = context.get(response.dict["AdditionalDataURI"])
    return (
        filename,
        response._http_response.content,
    )  # TODO: May need to push support in python-redfish-library to have a proper method of getting raw content
