#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Systems Module

File : root.py

Brief : This file contains the definitions and functionalities for interacting
        with the root level collection for a given Redfish service
"""

from .messages import verify_response


class RedfishNoResourceError(Exception):
    """
    Raise can't find resource error
    """
    pass


class RedfishCommonError(Exception):
    """
    Raise common error
    """
    pass


def get_resource_ids(context, resource_name):
    """
    Finds the resource collection and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session
        resource_name: The name of the resource collection

    Returns:
        A list of identifiers of the members of the resource collection
    """

    # Get the service root to find the system collection
    service_root = context.get("/redfish/v1/")
    if resource_name not in service_root.dict:
        # No such collection
        raise RedfishNoResourceError("Redfish does not contain a resource collection '{}'".format(resource_name))

    # Get the resource collection and iterate through its collection
    avail_resources = []
    resource_col = context.get(service_root.dict[resource_name]["@odata.id"])
    while True:
        for resource_member in resource_col.dict["Members"]:
            avail_resources.append(resource_member["@odata.id"].strip("/").split("/")[-1])
        if "Members@odata.nextLink" not in resource_col.dict:
            break
        resource_col = context.get(resource_col.dict["Members@odata.nextLink"])
    return avail_resources


def get_root_level_resource(context, resource_name, resource_id=None):
    """
    Finds a resource matching the given identifier from a top level resource collection matching the given
    resource_name and resource_id (if have), and returns it

    Args:
        context: The Redfish client object with an open session
        resource_name: The name of the root level resource collection to get
        resource_id: The resource member id to locate; if None, perform on the only member

    Returns:
        The resource in the resource collection
    """

    resource_uri_pattern = "/redfish/v1/" + resource_name + '/{}'
    avail_resource = None

    # If given an member id, get the resource directly
    if resource_id is not None:
        resource = context.get(resource_uri_pattern.format(resource_id))
    # No member id given; see if there's exactly one member
    else:
        avail_resource = get_resource_ids(context, resource_name)
        if len(avail_resource) == 1:
            resource = context.get(resource_uri_pattern.format(avail_resource[0]))
        else:
            raise RedfishCommonError("Redfish does not contain exactly one resource; a target resource needs "
                                     "to be specified: {}".format(", ".join(avail_resource)))

    # Check the response and return the system if the response is good
    try:
        verify_response(resource)
    except:
        if avail_resource is None:
            avail_resource = get_resource_ids(context, resource_name)
        raise RedfishNoResourceError("{} resource collection does not contain a resource called {}; valid resources: {}"
                                     .format(resource_name, resource_id, ", ".join(avail_resource))) from None
    return resource
