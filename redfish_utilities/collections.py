#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Collections Module

File : collections.py

Brief : This file contains the definitions and functionalities for performing
        operations with resource collections
"""

from .messages import verify_response


class RedfishCollectionNotFoundError(Exception):
    """
    Raised when the specified collection is not found (HTTP Status = 404)
    """

    pass


class RedfishCollectionMemberNotFoundError(Exception):
    """
    Raised when the specified member is not found (HTTP Status = 404)
    """

    pass


def get_collection_ids(context, collection_uri):
    """
    Iterates over a collection and returns the identifiers of all members

    Args:
        context: The Redfish client object with an open session
        collection_uri: The URI of the collection to process

    Returns:
        A list of identifiers of the members of the collection
    """

    # Get the collection and iterate through its collection
    avail_members = []
    collection = context.get(collection_uri)
    if collection.status == 404:
        raise RedfishCollectionNotFoundError("Service does not contain a collection at URI {}".format(collection_uri))
    verify_response(collection)
    while True:
        for member in collection.dict["Members"]:
            avail_members.append(member["@odata.id"].strip("/").split("/")[-1])
        if "Members@odata.nextLink" not in collection.dict:
            break
        collection = context.get(collection.dict["Members@odata.nextLink"])
        verify_response(collection)

    return avail_members


def get_collection_members(context, collection_uri):
    """
    Iterates over a collection and returns all members

    Args:
        context: The Redfish client object with an open session
        collection_uri: The URI of the collection to process

    Returns:
        A list of the members of the collection
    """

    # Get the collection and iterate through its collection
    members = []
    collection = context.get(collection_uri)
    if collection.status == 404:
        raise RedfishCollectionNotFoundError("Service does not contain a collection at URI {}".format(collection_uri))
    verify_response(collection)
    while True:
        for member in collection.dict["Members"]:
            member_response = context.get(member["@odata.id"])
            verify_response(member_response)
            members.append(member_response.dict)
        if "Members@odata.nextLink" not in collection.dict:
            break
        collection = context.get(collection.dict["Members@odata.nextLink"])
        verify_response(collection)

    return members
