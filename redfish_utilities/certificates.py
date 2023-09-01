#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2023 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Certificates Module

File : certificates.py

Brief : This file contains the definitions and functionalities for managing
        certificates on a Redfish service
"""

import os
from .messages import verify_response

class RedfishCertificateServiceNotFoundError( Exception ):
    """
    Raised when the certificate service cannot be found
    """
    pass

class RedfishCertificateLocationsNotFoundError( Exception ):
    """
    Raised when the certificate locations cannot be found
    """
    pass

class RedfishGenerateCSRActionNotFoundError( Exception ):
    """
    Raised when the GenerateCSR action cannot be found
    """
    pass

class RedfishReplaceCertificateActionNotFoundError( Exception ):
    """
    Raised when the ReplaceCertificate action cannot be found
    """
    pass

def get_all_certificates( context ):
    """
    Collects certificate information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list containing all certificates
    """

    certificate_list = []

    # Get the certificate locations
    certificate_service = get_certificate_service( context )
    if "CertificateLocations" not in certificate_service:
        raise RedfishCertificateLocationsNotFoundError( "Service does not contain certificate locations" )
    certificate_locations = context.get( certificate_service["CertificateLocations"]["@odata.id"] )
    verify_response( certificate_locations )

    # Get each member and add it to the response list
    locations = certificate_locations.dict.get( "Links", {} ).get( "Certificates", [] )
    for certificate_ref in locations:
        certificate = context.get( certificate_ref["@odata.id"] )
        verify_response( certificate )
        certificate_info = {
            "URI": certificate.dict["@odata.id"],
            "Id": certificate.dict["Id"],
            "Subject": certificate.dict.get( "Subject", {} ),
            "Issuer": certificate.dict.get( "Issuer", {} ),
            "ValidNotBefore": certificate.dict.get( "ValidNotBefore" ),
            "ValidNotAfter": certificate.dict.get( "ValidNotAfter" ),
            "KeyUsage": certificate.dict.get( "KeyUsage" ),
            "SerialNumber": certificate.dict.get( "SerialNumber" ),
            "Fingerprint": certificate.dict.get( "Fingerprint" ),
            "FingerprintHashAlgorithm": certificate.dict.get( "FingerprintHashAlgorithm" ),
            "SignatureAlgorithm": certificate.dict.get( "SignatureAlgorithm" ),
            "CertificateUsageTypes": certificate.dict.get( "CertificateUsageTypes" )
        }
        certificate_list.append( certificate_info )

    return certificate_list

def print_certificates( certificate_list, details = False ):
    """
    Prints the certificate list into a table

    Args:
        certificate_list: The certificate list to print
        details: True to print all the detailed info
    """

    # Go through each certificate
    for certificate in certificate_list:
        print( "Certificate: {}".format( certificate["URI"] ) )
        print( "  Subject: {}".format( build_identifier_string( certificate["Subject"] ) ) )
        print( "  Issuer: {}".format( build_identifier_string( certificate["Issuer"] ) ) )
        print( "  Valid Not Before: {}, Valid Not After: {}".format( certificate["ValidNotBefore"], certificate["ValidNotAfter"] ) )
        if details:
            if certificate["KeyUsage"] is not None:
                print( "  Key Usage: {}".format( ", ".join( certificate["KeyUsage"] ) ) )
            if certificate["CertificateUsageTypes"] is not None:
                print( "  Certificate Usage: {}".format( ", ".join( certificate["CertificateUsageTypes"] ) ) )
            if certificate["SerialNumber"] is not None:
                print( "  Serial Number: {}".format( certificate["SerialNumber"] ) )
            if certificate["Fingerprint"] is not None:
                print( "  Fingerprint: {}".format( certificate["Fingerprint"] ) )
            if certificate["FingerprintHashAlgorithm"] is not None:
                print( "  Fingerprint Hash Algorithm: {}".format( certificate["FingerprintHashAlgorithm"] ) )
            if certificate["SignatureAlgorithm"] is not None:
                print( "  Signature Algorithm: {}".format( certificate["SignatureAlgorithm"] ) )
        print( "" )

def get_generate_csr_info( context ):
    """
    Finds information about the support for generating CSRs

    Args:
        context: The Redfish client object with an open session

    Returns:
        The URI of the GenerateCSR action
        A list of parameter requirements from the action info
    """

    # Check that there is a GenerateCSR action
    certificate_service = get_certificate_service( context )
    if "Actions" not in certificate_service:
        raise RedfishGenerateCSRActionNotFoundError( "Service does not support the GenerateCSR action" )
    if "#CertificateService.GenerateCSR" not in certificate_service["Actions"]:
        raise RedfishGenerateCSRActionNotFoundError( "Service does not support the GenerateCSR action" )

    # Extract the info about the GenerateCSR action
    generate_csr_action = certificate_service["Actions"]["#CertificateService.GenerateCSR"]
    generate_csr_uri = generate_csr_action["target"]

    if "@Redfish.ActionInfo" not in generate_csr_action:
        # No action info; due to the action's complexity, don't try to produce a default set of parameters
        generate_csr_parameters = None
    else:
        # Get the action info and its parameter listing
        action_info = context.get( generate_csr_action["@Redfish.ActionInfo"] )
        generate_csr_parameters = action_info.dict["Parameters"]

    return generate_csr_uri, generate_csr_parameters

def generate_csr( context, common_name, organization, organizational_unit, city, state, country, cert_col, email = None, key_pair_alg = None, key_bit_len = None, key_curve_id = None ):
    """
    Generates a certificate signing request

    Args:
        context: The Redfish client object with an open session
        common_name: The common name of the component to secure
        organization: The name of the organization making the request
        organizational_unit: The name of the unit in the organization making the request
        city: The city or locality of the organization making the request
        state: The state, province, or region of the organization making the request
        country: The two-letter country code of the organization making the request
        cert_col: The URI of the certificate collection where the signed certificate will be installed
        email: The email address of the contact within the organization making the request
        key_pair_alg: The type of key-pair for use with signing algorithms
        key_bit_len: The length of the key, in bits, if the key pair algorithm supports key size
        key_curve_id: The curve ID to use with the key if the key pair algorithm supports curves

    Returns:
        The response of the action
    """

    # Locate the GenerateCSR action
    generate_csr_uri, generate_csr_parameters = get_generate_csr_info( context )

    # Build the payload
    payload = {
        "CertificateCollection": { "@odata.id": cert_col },
        "CommonName": common_name,
        "Organization": organization,
        "OrganizationalUnit": organizational_unit,
        "City": city,
        "State": state,
        "Country": country
    }
    if email is not None:
        payload["Email"] = email
    if key_pair_alg is not None:
        payload["KeyPairAlgorithm"] = key_pair_alg
    if key_bit_len is not None:
        payload["KeyBitLength"] = key_bit_len
    if key_curve_id is not None:
        payload["KeyCurveId"] = key_curve_id

    # Generate a CSR
    response = context.post( generate_csr_uri, body = payload )
    verify_response( response )
    return response

def install_certificate( context, destination, cert_file, key_file = None ):
    """
    Replaces an existing certificate with a new certificate

    Args:
        context: The Redfish client object with an open session
        destination: The installation URI of the certificate; either a certificate collection to insert, or an existing certificate to replace
        cert_file: The file, and optional path, of the certificate to install
        key_file: The file, and optional path, of the private key for the certificate to install

    Returns:
        The response of the operation
    """

    # Read the certificate and determine its type
    with open( cert_file, "r" ):
         cert_string = cert_file.read()
    cert_type = "PEM"
    if "BEGIN PKCS7" in cert_string:
        cert_type = "PKCS7"
    elif cert_string.count( "BEGIN CERTIFICATE" ) > 1:
        cert_type = "PEMchain"

    # Read the key if needed, and prepend it to the certificate
    if key_file is not None:
        with open( cert_file, "r" ):
            key_string = key_file.read()
        cert_string = key_string + cert_string

    # Build the payload
    payload = {
        "CertificateUri": { "@odata.id": destination },
        "CertificateString": cert_string,
        "CertificateType": cert_type
    }

    # Check if the referenced destination is a certificate collection or individual certificate
    dest_response = context.get( destination )
    verify_response( dest_response )
    if dest_response.dict["@odata.type"] == "#CertificateCollection.CertificateCollection":
        # Certificate collection; just perform a POST operation on the collection
        payload.pop( "CertificateUri" )
    else:
        # Individual certificate; perform a replacement operation from the certificate service

        # Locate the ReplaceCertificate action
        certificate_service = get_certificate_service( context )
        if "Actions" not in certificate_service:
            raise RedfishReplaceCertificateActionNotFoundError( "Service does not support the ReplaceCertificate action" )
        if "#CertificateService.ReplaceCertificate" not in certificate_service["Actions"]:
            raise RedfishReplaceCertificateActionNotFoundError( "Service does not support the ReplaceCertificate action" )
        destination = certificate_service["Actions"]["#CertificateService.ReplaceCertificate"]["target"]

    # Install the certificate
    response = context.post( destination, body = payload )
    verify_response( response )
    return response

def delete_certificate( context, certificate ):
    """
    Replaces an existing certificate with a new certificate

    Args:
        context: The Redfish client object with an open session
        certificate: The URI of the certificate to delete

    Returns:
        The response of the operation
    """

    # Delete the certificate
    response = context.delete( certificate )
    verify_response( response )
    return response

def get_certificate_service( context ):
    """
    Collects the certificate service information from a Redfish service

    Args:
        context: The Redfish client object with an open session

    Returns:
        An object containing information about the certificate service
    """

    # Get the service root to find the certificate service
    service_root = context.get( "/redfish/v1/" )
    if "CertificateService" not in service_root.dict:
        # No event service
        raise RedfishCertificateServiceNotFoundError( "Service does not contain a certificate service" )

    # Get the certificate service
    certificate_service = context.get( service_root.dict["CertificateService"]["@odata.id"] )
    verify_response( certificate_service )
    return certificate_service.dict

def build_identifier_string( identifier ):
    """
    Creates an identifier string for a subject or issuer object

    Args:
        identifier: The identifier object to parse

    Returns:
        A string containing the identifier info
    """

    field_map = {
        "CommonName": "CN",
        "Organization": "O",
        "OrganizationalUnit": "OU",
        "Country": "C",
        "State": "ST",
        "City": "L",
        "Email": "emailAddress"
    }

    strings = []
    for map in field_map:
        if map in identifier and identifier[map] is not None:
            strings.append( "{}={}".format( field_map[map], identifier[map] ) )
    return ", ".join( strings )
