#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Event Service Module

File : event_service.py

Brief : This file contains the definitions and functionalities for managing
        accounts on a Redfish Service
"""

from .messages import verify_response

class RedfishEventServiceNotFoundError( Exception ):
    """
    Raised when the event service cannot be found
    """
    pass

class RedfishEventSubscriptionNotFoundError( Exception ):
    """
    Raised when the specified event subscription cannot be found
    """
    pass

def get_event_service( context ):
    """
    Collects the event service information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        An object containing information about the event service
    """

    # Get the service root to find the event service
    service_root = context.get( "/redfish/v1/" )
    if "EventService" not in service_root.dict:
        # No event service
        raise RedfishEventServiceNotFoundError( "Service does not contain an event service" )

    # Get the event service
    event_service = context.get( service_root.dict["EventService"]["@odata.id"] )
    return event_service.dict

def print_event_service( service ):
    """
    Prints the event service information from a Redfish service

    Args:
        service: The event service object
    """

    print( "Service Info" )

    # General status
    status = "Enabled"
    if "ServiceEnabled" in service:
        if not service["ServiceEnabled"]:
            status = "Disabled"
    if "Status" in service:
        if "State" in service["Status"]:
            status = service["Status"]["State"]
    print( "  Status: {}".format( status ) )

    # Delivery retry policy
    retry_policy = ""
    if "DeliveryRetryAttempts" in service:
        retry_policy += "{} attempts, ".format( service["DeliveryRetryAttempts"] )
    if "DeliveryRetryIntervalSeconds" in service:
        retry_policy += "{} second intervals, ".format( service["DeliveryRetryIntervalSeconds"] )
    if len( retry_policy ) > 2:
        retry_policy = retry_policy[:-2]
    else:
        retry_policy = "Unknown/Unspecified"
    print( "  Delivery Retry Policy: {}".format( retry_policy ) )

    # Subscription methods
    print( "  Event Types: {}".format( ", ".join( service.get( "EventTypesForSubscription", [ "N/A" ] ) ) ) )
    print( "  Event Formats: {}".format( ", ".join( service.get( "EventFormatTypes", [ "N/A" ] ) ) ) )
    print( "  Registries: {}".format( ", ".join( service.get( "RegistryPrefixes", [ "N/A" ] ) ) ) )
    print( "  Resource Types: {}".format( ", ".join( service.get( "ResourceTypes", [ "N/A" ] ) ) ) )
    print( "  Include Origin of Condition Supported: {}".format( service.get( "IncludeOriginOfConditionSupported", False ) ) )

    # SSE info
    print( "  SSE URI: {}".format( service.get( "ServerSentEventUri", "Not supported" ) ) )
    sse_filters = ""
    for filter in service.get( "SSEFilterPropertiesSupported", {} ):
        if filter == "EventType":
            # This style is deprecated
            continue
        if service["SSEFilterPropertiesSupported"][filter]:
            sse_filters += "{}, ".format( filter )
    if len( sse_filters ) > 2:
        sse_filters = sse_filters[:-2]
    else:
        sse_filters = "Unknown/Unspecified"
    print( "  SSE Filter Parameters: {}".format( sse_filters ) )

def get_event_subscriptions( context ):
    """
    Collects the event subscription information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all event subscriptions
    """

    # Get the event service
    event_service = get_event_service( context )
    if "Subscriptions" not in event_service:
        # No subscriptions
        raise RedfishEventServiceNotFoundError( "Service does not contain a subscription collection" )

    # Get each of the event subscriptions
    subscriptions = []
    subscription_col = context.get( event_service["Subscriptions"]["@odata.id"] )
    for subscription_member in subscription_col.dict["Members"]:
        subscription = context.get( subscription_member["@odata.id"] )
        subscriptions.append( subscription.dict )
    return subscriptions

def print_event_subscriptions( subscriptions ):
    """
    Prints the event subscription information from a Redfish service

    Args:
        subscriptions: An array of event subscription objects
    """

    subscription_line_format = "  {:36s} | {}: {}"

    print( "Subscription Info" )

    if len( subscriptions ) == 0:
        print( "  No subscriptions" )
        return

    for subscription in subscriptions:
        print( subscription_line_format.format( subscription["Id"], "Destination", subscription.get( "Destination", "N/A" ) ) )
        print( subscription_line_format.format( "", "State", subscription.get( "Status", {} ).get( "State", "Enabled" ) ) )
        if "Context" in subscription:
            print( subscription_line_format.format( "", "Context", subscription["Context"] ) )
        print( subscription_line_format.format( "", "Event Format", subscription.get( "EventFormatType", "Event" ) ) )
        if "EventTypes" in subscription:
            print( subscription_line_format.format( "", "Event Types", ", ".join(subscription["EventTypes"] ) ) )
        if "RegistryPrefixes" in subscription:
            print( subscription_line_format.format( "", "Registries", ", ".join( subscription["RegistryPrefixes"] ) ) )
        if "ResourceTypes" in subscription:
            print( subscription_line_format.format( "", "Resource Types", ", ".join( subscription["ResourceTypes"] ) ) )

def create_event_subscription( context, destination, format = None, client_context = None, expand = None, resource_types = None,
    registries = None, message_ids = None, origins = None, subordinate_resources = None, event_types = None ):
    """
    Creates an event subscription

    Args:
        context: The Redfish client object with an open session
        destination: The event subscription destination
        format: The format of the event payloads
        client_context: The client-provided context string
        expand: Indicates if the OriginOfCondition is to be expanded in event payloads
        resource_types: The resource types for the subscription
        registries: The registries for the subscription
        message_ids: The message IDs for the subscription
        origins: The origins for the subscription
        subordinate_resources: Indicates if subordinate resources to those referenced by 'origins' will also be monitored
        event_types: The event types for the subscription; this method for subscriptions has been deprecated for other controls

    Returns:
        The response of the POST
    """

    # Get the event service
    event_service = get_event_service( context )
    if "Subscriptions" not in event_service:
        # No subscriptions
        raise RedfishEventServiceNotFoundError( "Service does not contain a subscription collection" )

    # Form the POST request
    payload = {
        "Destination": destination,
        "Protocol": "Redfish"
    }
    if format is not None:
        payload["EventFormatType"] = format
    if client_context is not None:
        payload["Context"] = client_context
    if expand is not None:
        payload["IncludeOriginOfCondition"] = expand
    if resource_types is not None:
        payload["ResourceTypes"] = resource_types
    if registries is not None:
        payload["RegistryPrefixes"] = registries
    if message_ids is not None:
        payload["MessageIds"] = message_ids
    if origins is not None:
        payload["OriginResources"] = origins
    if subordinate_resources is not None:
        payload["SubordinateResources"] = subordinate_resources
    if event_types is not None:
        payload["EventTypes"] = event_types

    # Create the subscription
    response = context.post( event_service["Subscriptions"]["@odata.id"], body = payload )
    verify_response( response )
    return response

def delete_event_subscription( context, id ):
    """
    Deletes an event subscription

    Args:
        context: The Redfish client object with an open session
        id: The identifier for the subscription

    Returns:
        The response of the DELETE
    """

    # Get the current subscriptions
    subscriptions = get_event_subscriptions( context )

    # Find the matching subscription and delete it
    for subscription in subscriptions:
        if subscription["Id"] == id:
            response = context.delete( subscription["@odata.id"] )
            verify_response( response )
            return response

    # No matches found
    raise RedfishEventSubscriptionNotFoundError( "Service does not contain an event subscription called {}".format( id ) )
