#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2026 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Component Integrity Module

File : component_integrity.py

Brief : This file contains the definitions and functionalities for performing
        operations with component integrity for a given Redfish service
"""

import base64
import os

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import ec, rsa, utils
from cryptography import x509
from OpenSSL import crypto

from .collections import get_collection_ids, get_collection_member, get_collection_members
from .messages import verify_response


class RedfishComponentIntegrityGetSignedMeasurementsNotFoundError(Exception):
    """
    Raised when the component integrity instance does not support getting signed measurements
    """

    pass


class RedfishInvalidSignedMeasurements(Exception):
    """
    Raised when the signed measurements cannot be parsed or verified
    """

    pass


_component_integrity_uri_collection = "/redfish/v1/ComponentIntegrity"


# Comes from DSP0274: "SPDM Asymmetric Signature Reference Information" table
_spdm_signature_sizes_bytes = {
    "TPM_ALG_RSASSA_3072": 384,
    "TPM_ALG_RSASSA_4096": 512,
    "TPM_ALG_RSAPSS_2048": 256,
    "TPM_ALG_RSAPSS_3072": 384,
    "TPM_ALG_RSAPSS_4096": 512,
    "TPM_ALG_ECDSA_ECC_NIST_P256": 64,
    "TPM_ALG_ECDSA_ECC_NIST_P384": 96,
    "TPM_ALG_ECDSA_ECC_NIST_P521": 132,
    "EdDSA ed25519": 64,
    "EdDSA ed448": 114,
    "ML-DSA-44": 2420,
    "ML-DSA-65": 3309,
    "ML-DSA-87": 4627,
    "SLH-DSA-SHA2-128s": 7856,
    "SLH-DSA-SHAKE-128s": 7856,
    "SLH-DSA-SHA2-128f": 17088,
    "SLH-DSA-SHAKE-128f": 17088,
    "SLH-DSA-SHA2-192s": 16224,
    "SLH-DSA-SHAKE-192s": 16224,
    "SLH-DSA-SHA2-192f": 35664,
    "SLH-DSA-SHAKE-192f": 35664,
    "SLH-DSA-SHA2-256s": 29792,
    "SLH-DSA-SHAKE-256s": 29792,
    "SLH-DSA-SHA2-256f": 49856,
    "SLH-DSA-SHAKE-256f": 49856,
}


# Comes from DSP0274: "BaseHashAlgo" field in "NEGOTIATE_ALGORITHMS"
_spdm_hash_algorithms = {
    "TPM_ALG_SHA_256": hashes.SHA256(),
    "TPM_ALG_SHA_384": hashes.SHA384(),
    "TPM_ALG_SHA_512": hashes.SHA512(),
    "TPM_ALG_SHA3_256": hashes.SHA3_256(),
    "TPM_ALG_SHA3_384": hashes.SHA3_384(),
    "TPM_ALG_SHA3_512": hashes.SHA3_512(),
    "TPM_ALG_SM3_256": hashes.SM3(),
}


def get_component_integrity_summary(context):
    """
    Gets a summary of all component integrity instances

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list of dictionaries containing summary info for each component integrity instance
    """

    component_integrity_summary = []

    # Get all component integrity resources
    component_integrity_members = get_collection_members(context, _component_integrity_uri_collection)

    for component_integrity in component_integrity_members:
        summary = {
            "Id": component_integrity.get("Id"),
            "Name": component_integrity.get("Name"),
            "ComponentIntegrityType": component_integrity.get("ComponentIntegrityType"),
            "TargetComponentURI": component_integrity.get("TargetComponentURI"),
            "State": component_integrity.get("Status", {}).get("State"),
            "Health": component_integrity.get("Status", {}).get("Health"),
        }
        component_integrity_summary.append(summary)

    return component_integrity_summary


def print_component_integrity_summary(component_integrity_summary):
    """
    Prints the component integrity summary into a table

    Args:
        component_integrity_summary: The component integrity summary to print
    """

    summary_line_title_format = "  {:16s} | {}"
    summary_line_target_format = "  {:16s} | Component: {}"
    summary_line_detail_format = "  {:16s} | Type: {}; State: {}/{}"

    if len(component_integrity_summary) == 0:
        print("  No component integrity instances")
        return

    print(summary_line_title_format.format("Id", "Details"))
    for component_integrity in component_integrity_summary:
        print(summary_line_title_format.format(component_integrity["Id"], component_integrity["Name"]))
        print(summary_line_target_format.format("", component_integrity["TargetComponentURI"] if component_integrity["TargetComponentURI"] else "Unknown"))
        print(summary_line_detail_format.format("", component_integrity["ComponentIntegrityType"] if component_integrity["ComponentIntegrityType"] else "Unknown", component_integrity["State"] if component_integrity["State"] else "Unknown", component_integrity["Health"] if component_integrity["Health"] else "Unknown"))
    print("")


def get_component_integrity_ids(context):
    """
    Finds the component integrity collection and returns all of the member's identifiers

    Args:
        context: The Redfish client object with an open session

    Returns:
        A list of identifiers of the members of the component integrity collection
    """

    return get_collection_ids(context, _component_integrity_uri_collection)


def get_component_integrity(context, component_integrity_id):
    """
    Finds a component integrity matching the given identifier and returns its resource

    Args:
        context: The Redfish client object with an open session
        component_integrity_id: The component integrity instance to locate

    Returns:
        The component integrity resource
    """

    return get_collection_member(context, _component_integrity_uri_collection, component_integrity_id)


def get_signed_measurements(context, component_integrity_id, nonce=None, certificate_uri=None):
    """
    Gets the signed measurements for a component integrity instance

    Args:
        context: The Redfish client object with an open session
        id: The ID of the component integrity instance
        nonce: The nonce to use for the request
        certificate_uri: The URI of the certificate to use for signing the measurements

    Returns:
        The response of the action
        Context info for processing the response
    """

    # Get the component integrity resource
    component_integrity = get_component_integrity(context, component_integrity_id)
    body = None
    certificate = None

    # Locate the signed measurements action
    if "Actions" not in component_integrity:
        raise RedfishComponentIntegrityGetSignedMeasurementsNotFoundError("Component integrity '{}' does not support getting signed measurements".format(component_integrity_id))
    if component_integrity["ComponentIntegrityType"] == "SPDM":
        # SPDM path
        if "#ComponentIntegrity.SPDMGetSignedMeasurements" not in component_integrity["Actions"]:
            raise RedfishComponentIntegrityGetSignedMeasurementsNotFoundError("Component integrity '{}' does not support getting signed measurements".format(component_integrity_id))
        target_uri = component_integrity["Actions"]["#ComponentIntegrity.SPDMGetSignedMeasurements"]["target"]
        if nonce is None:
            # We always want to provide a nonce
            nonce = os.urandom(32).hex()
        body = { "Nonce": nonce }
        if certificate_uri is not None:
            # If a certificate was specified, get its slot ID
            certificate = context.get(certificate_uri)
            verify_response(certificate)
            body["SlotId"] = certificate.dict["SPDM"]["SlotId"]
            certificate = certificate.dict
    else:
        # Others (no support yet)
        raise NotImplementedError("Signed measurements for '{}' are not supported".format(component_integrity["ComponentIntegrityType"]))

    # Perform the action request
    response = context.post(target_uri, body=body)
    verify_response(response)
    action_context = {
        "ComponentIntegrity": component_integrity,
        "Payload": body,
        "Certificate": certificate,
    }
    return response, action_context


def parse_signed_measurements(response, action_context):
    """
    Parses the signed measurements response

    Args:
        response: The response of the action
        action_context: Context info for processing the response

    Returns:
        The parsed signed measurements
    """

    # Copy the response body and pertinent action context
    measurements = dict(response.dict)
    measurements["RequestBody"] = action_context["Payload"]
    measurements["RequestCertificate"] = action_context["Certificate"]
    measurements["ComponentIntegrity"] = action_context["ComponentIntegrity"]

    # Parse the measurements based on the type of device
    if action_context["ComponentIntegrity"]["ComponentIntegrityType"] == "SPDM":
        # SPDM path
        measurements["Type"] = "SPDM"
        measurements["VCA"], measurements["Measurements"], measurements["MeasurementLog"], measurements["Signature"], measurements["RequestNonce"] = _parse_spdm_signed_measurements(measurements["Version"], measurements["SigningAlgorithm"], measurements["SignedMeasurements"])
    else:
        # Others (no support yet)
        raise NotImplementedError("Signed measurements for '{}' are not supported".format(action_context["ComponentIntegrity"]["ComponentIntegrityType"]))

    return measurements


def print_signed_measurements(parsed_measurements):
    """
    Prints previously parsed signed measurements

    Args:
        parsed_measurements: The parsed signed measurements to print
    """

    if parsed_measurements["Type"] == "SPDM":
        print("Signed Measurements:")
        print("  Type: {}".format(parsed_measurements["Type"]))
        print("  SPDM Version: {}".format(parsed_measurements["Version"]))
        print("  Signing Algorithm: {}".format(parsed_measurements["SigningAlgorithm"]))
        print("  Hashing Algorithm: {}".format(parsed_measurements["HashingAlgorithm"]))
        print("")
        if parsed_measurements["VCA"] is not None:
            print("  Supported Versions: {}".format(", ".join(parsed_measurements["VCA"]["SupportedVersions"])))
            print("  Requester Size Limits: Max Transfer Size: {}, Max Message Size: {}".format(parsed_measurements["VCA"]["RequesterMaxMessageSize"], parsed_measurements["VCA"]["RequesterMaxMessageSize"]))
            print("  Responder Size Limits: Max Transfer Size: {}, Max Message Size: {}".format(parsed_measurements["VCA"]["ResponderMaxMessageSize"], parsed_measurements["VCA"]["ResponderMaxMessageSize"]))
            print("")
        print("  Measurements:")
        for i, measurement in enumerate(parsed_measurements["Measurements"]):
            print("    Index: {}, Specification: {:02x}".format(measurement["Index"], measurement["MeasurementSpecification"]))
            print("    Data: {}".format(measurement["Measurement"].hex()))
        print("")
    else:
        # Others (no support yet)
        raise NotImplementedError("Signed measurements for '{}' are not supported".format(parsed_measurements["Type"]))


def verify_signed_measurements(context, parsed_measurements):
    """
    Verifies previously parsed signed measurements

    Args:
        context: The Redfish client context
        parsed_measurements: The parsed signed measurements to verify
    """

    # Verification relies on the type of signed measurements
    if parsed_measurements["Type"] == "SPDM":
        # Check that the request nonce found in the response matches what was provided in the original request
        if "Nonce" in parsed_measurements["RequestBody"]:
            if parsed_measurements["RequestNonce"] is None:
                raise RedfishInvalidSignedMeasurements("The request nonce is missing from the measurement log")
            if parsed_measurements["RequestNonce"].hex().lower() != parsed_measurements["RequestBody"]["Nonce"].lower():
                raise RedfishInvalidSignedMeasurements("The request nonce does not match the nonce found in the measurement log")

        # Check that the certificate chain is valid
        # Preference order:
        # 1) Certificate used in the request
        # 2) Certificate referenced from the action response
        # 3) The device certificate referenced by the resource
        certificate = None
        if parsed_measurements["RequestCertificate"] is not None:
            # Case 1: Just use the existing certificate resource data
            certificate = parsed_measurements["RequestCertificate"]
        elif "Certificate" in parsed_measurements:
            # Case 2: Follow the link from the action response
            resp = context.get(parsed_measurements["Certificate"]["@odata.id"])
            verify_response(resp)
            certificate = resp.dict
        else:
            # Case 3: Follow the link from SPDM/IdentityAuthentication/ResponderAuthentication/ComponentCertificate
            try:
                cert_uri = parsed_measurements["ComponentIntegrity"]["SPDM"]["IdentityAuthentication"]["ResponderAuthentication"]["ComponentCertificate"]["@odata.id"]
            except Exception:
                raise RedfishInvalidSignedMeasurements("No device certificate found")
            resp = context.get(cert_uri)
            verify_response(resp)
            certificate = resp.dict
        # Get the certificate chain and break it into individual certificates
        if "CertificateString" not in certificate:
            raise RedfishInvalidSignedMeasurements("No certificate string found to verify measurements")
        cert_delim = "-----END CERTIFICATE-----"
        cert_chain_raw = [cert + cert_delim for cert in certificate["CertificateString"].strip().split(cert_delim) if cert]

        # Go through the chain, starting with the root certificate, and verify each certificate
        cert_store = crypto.X509Store()
        for cert_str in reversed(cert_chain_raw):
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_str)
                cert_store.add_cert(cert)
                store_context = crypto.X509StoreContext(cert_store, cert)
                store_context.verify_certificate()
            except Exception as e:
                raise RedfishInvalidSignedMeasurements("Failed to verify the certificate chain: {}".format(e))

        # Get the public key from the certificate
        try:
            public_key = x509.load_pem_x509_certificate(cert_chain_raw[0].encode('utf-8')).public_key()
        except Exception:
            raise RedfishInvalidSignedMeasurements("Failed to load the public key from the certificate")

        # Verify the signature
        try:
            hash_algorithm = _spdm_hash_algorithms[parsed_measurements["HashingAlgorithm"]]
        except Exception:
            raise RedfishInvalidSignedMeasurements("Unknown hash algorithm: {}".format(parsed_measurements["HashingAlgorithm"]))
        try:
            # Verification is dependent on the key type
            if isinstance(public_key, ec.EllipticCurvePublicKey):
                # ECDSA signatures require breaking down the signature in to a DER-encoded format
                # It also requires the hash algorithm to be provided
                sig_half = int(len(parsed_measurements["Signature"]) / 2)
                r = int.from_bytes(parsed_measurements["Signature"][:sig_half], byteorder="big")
                s = int.from_bytes(parsed_measurements["Signature"][sig_half:], byteorder="big")
                public_key.verify(utils.encode_dss_signature(r, s), parsed_measurements["MeasurementLog"], ec.ECDSA(hash_algorithm))
            elif isinstance(public_key, rsa.RSAPublicKey):
                # RSA signatures require the padding and hash algorithm to be provided
                public_key.verify(parsed_measurements["Signature"], parsed_measurements["MeasurementLog"], padding.PKCS1v15(), hash_algorithm)
            else:
                # Other key types don't require additional info
                # The cryptography module uses this for the following key types: Ed448, Ed25519, and ML-DSA
                # SLH-DSA is currently not supported, but anticipating the same pattern will be used when it's added
                public_key.verify(parsed_measurements["Signature"], parsed_measurements["MeasurementLog"])
        except Exception:
            raise RedfishInvalidSignedMeasurements("Failed to verify the signature with the public key")
    else:
        # Others (no support yet)
        raise NotImplementedError("Signed measurements for '{}' are not supported".format(parsed_measurements["Type"]))


def _parse_spdm_signed_measurements(version, signing_algorithm, raw_measurements):
    """
    Parses an SPDM signed measurement transcript from the SPDMGetSignedMeasurements action response

    Args:
        version: The version string of the SPDM protocol
        signing_algorithm: The signing algorithm used by the SPDM responder
        raw_measurements: The raw measurements data as a Base64-encoded string

    Returns:
        A dictionary of the VCA transcript; None if the SPDM version is less than 1.2
        A list of dictionaries containing the measurements
        A byte array containing the measurement log data
        A byte array containing the signature of the measurement log data
        A byte array containing the request nonce
    """

    # Decode the measurement data into raw bytes
    try:
        data = base64.b64decode(raw_measurements)
    except Exception:
        raise RedfishInvalidSignedMeasurements("Invalid Base64 data: {}".format(raw_measurements))

    # Parse the SPDM version
    try:
        # Wanted to keep the version parsing/comparison simple without bringing in packaging or other dependencies
        version_num = int(version.split(".")[0]) * 100 + int(version.split(".")[1])
    except Exception:
        raise RedfishInvalidSignedMeasurements("Invalid SPDM version: {}".format(version))

    offset = 0
    vca = None
    measurements = []
    request_nonce = None
    signature_found = False

    # Separate the signature from the measurement data
    try:
        signature_len = _spdm_signature_sizes_bytes[signing_algorithm]
    except Exception:
        raise RedfishInvalidSignedMeasurements("Unknown signing algorithm: {}".format(signing_algorithm))
    try:
        signature = data[-signature_len:]
        measurement_log = data[:-signature_len]
    except Exception:
        raise RedfishInvalidSignedMeasurements("Could not separate signature from measurement data: {}".format(raw_measurements))

    try:
        if version_num >= 102:
            # SPDM 1.2+ includes VCA (Version, Capabilities, Algorithms)
            vca = {}
            offset = _spdm_parse_version_req_resp(data, offset, vca)
            offset = _spdm_parse_capabilities_req_resp(data, offset, version_num, vca)
            offset = _spdm_parse_algorithms_req_resp(data, offset, vca)

        # Go over all GET_MEASUREMENTS requests/MEASUREMENT responses
        while offset < len(data):
            # Only the last measurement should have a signature
            if signature_found:
                raise RedfishInvalidSignedMeasurements("Signature found in non-final measurement")
            offset, signature_found, request_nonce = _spdm_parse_measurement_req_resp(data, offset, version_num, signature_len, measurements)
    except RedfishInvalidSignedMeasurements:
        # Should already have a reasonable error message
        raise
    except Exception as e:
        # Wrap any other exceptions with a more specific message about unable to parse the SPDM messages
        raise RedfishInvalidSignedMeasurements("Error parsing SPDM messages: {}".format(e))

    # At least one measurement should have a signature
    if not signature_found:
        raise RedfishInvalidSignedMeasurements("No signature found in SPDM messages")

    return vca, measurements, measurement_log, signature, request_nonce


def _spdm_parse_version_req_resp(data, offset, vca):
    """
    Parses an SPDM GET_VERSION request and response pair

    Args:
        data: A byte array containing the measurement log
        offset: The starting offset into the measurement log to parse
        vca: The VCA dictionary to update

    Returns:
        An integer of the offset for the next structure in the measurement log
    """

    vca["SupportedVersions"] = []

    # GET_VERSION request
    # Check the request code is correct
    if data[offset + 1] != 0x84:  # GET_VERSION
        raise RedfishInvalidSignedMeasurements("Invalid GET_VERSION request code: 0x{:02X}".format(data[offset + 1]))
    offset += 4

    # VERSION response
    # Check the response code is correct
    if data[offset + 1] != 0x04:  # VERSION
        raise RedfishInvalidSignedMeasurements("Invalid VERSION response code: 0x{:02X}".format(data[offset + 1]))
    response_length = 6
    num_versions = data[offset + 5]
    response_length += (2 * num_versions)
    # Extract the supported SPDM versions; ignore the "Alpha" version
    for i in range(num_versions):
        version = "{}.{}.{}".format(
            (data[offset + 6 + 2 * i] >> 4) & 0xF,
            data[offset + 6 + 2 * i] & 0xF,
            (data[offset + 7 + 2 * i] >> 4) & 0xF,
        )
        vca["SupportedVersions"].append(version)
    offset += response_length

    return offset


def _spdm_parse_capabilities_req_resp(data, offset, version_num, vca):
    """
    Parses an SPDM GET_CAPABILITIES request and response pair

    Args:
        data: A byte array containing the measurement log
        offset: The starting offset into the measurement log to parse
        version_num: The SPDM version number
        vca: The VCA dictionary to update

    Returns:
        An integer of the offset for the next structure in the measurement log
    """

    vca["RequesterMaxTransferSize"] = None
    vca["RequesterMaxSPDMMessageSize"] = None
    vca["ResponderMaxTransferSize"] = None
    vca["ResponderMaxSPDMMessageSize"] = None

    # GET_CAPABILITIES request
    # Check the request code is correct
    if data[offset + 1] != 0xE1:  # GET_CAPABILITIES
        raise RedfishInvalidSignedMeasurements("Invalid GET_CAPABILITIES request code: 0x{:02X}".format(data[offset + 1]))
    if version_num == 100:
        offset += 4
    elif version_num == 101:
        offset += 12
    else:
        # SPDM 1.2+ has a transfer size fields
        vca["RequesterMaxTransferSize"] = int.from_bytes(data[offset + 12:offset + 16], byteorder="little")
        vca["RequesterMaxSPDMMessageSize"] = int.from_bytes(data[offset + 16:offset + 20], byteorder="little")
        offset += 20

    # CAPABILITIES response
    # Check the response code is correct
    if data[offset + 1] != 0x61:  # CAPABILITIES
        raise RedfishInvalidSignedMeasurements("Invalid CAPABILITIES response code: 0x{:02X}".format(data[offset + 1]))
    if version_num <= 101:
        offset += 12
    else:
        # SPDM 1.2+ has a transfer size fields
        vca["ResponderMaxTransferSize"] = int.from_bytes(data[offset + 12:offset + 16], byteorder="little")
        vca["ResponderMaxSPDMMessageSize"] = int.from_bytes(data[offset + 16:offset + 20], byteorder="little")
        alg_length = 0
        if version_num >= 103:
            # SPDM 1.3+ has an optional "supported algorithms" field
            if data[offset + 2] & 0x01:
                alg_length = int.from_bytes(data[offset + 22:offset + 24], byteorder="little")
        offset += 20 + alg_length

    return offset


def _spdm_parse_algorithms_req_resp(data, offset, vca):
    """
    Parses an SPDM NEGOTIATE_ALGORITHMS request and response pair

    Args:
        data: A byte array containing the measurement log
        offset: The starting offset into the measurement log to parse
        vca: The VCA dictionary to update

    Returns:
        An integer of the offset for the next structure in the measurement log
    """

    # NEGOTIATE_ALGORITHMS request
    # Check the request code is correct
    if data[offset + 1] != 0xE3:  # NEGOTIATE_ALGORITHMS
        raise RedfishInvalidSignedMeasurements("Invalid NEGOTIATE_ALGORITHMS request code: 0x{:02X}".format(data[offset + 1]))
    alg_length = int.from_bytes(data[offset + 4:offset + 6], byteorder="little")
    offset += alg_length

    # ALGORITHMS response
    # Check the response code is correct
    if data[offset + 1] != 0x63:  # ALGORITHMS
        raise RedfishInvalidSignedMeasurements("Invalid ALGORITHMS response code: 0x{:02X}".format(data[offset + 1]))
    alg_length = int.from_bytes(data[offset + 4:offset + 6], byteorder="little")
    offset += alg_length

    return offset


def _spdm_parse_measurement_req_resp(data, offset, version_num, signature_len, measurements):
    """
    Parses an SPDM GET_MEASUREMENTS request and response pair

    Args:
        data: A byte array containing the measurement log
        offset: The starting offset into the measurement log to parse
        version: The SPDM protocol version number
        signature_len: The length of the signature in bytes
        measurements: The current list of decoded measurements to update

    Returns:
        An integer of the offset for the next structure in the measurement log
        A boolean indicating if a signature was found in the response
        A byte array of the request nonce if found, otherwise None
    """

    # GET_MEASUREMENTS request
    # Check the request code is correct
    if data[offset + 1] != 0xE0:  # GET_MEASUREMENTS
        raise RedfishInvalidSignedMeasurements("Invalid GET_MEASUREMENTS request code: 0x{:02X}".format(data[offset + 1]))
    request_len = 4
    signature_found = bool(data[offset + 2] & 0x01)
    request_nonce = None
    if version_num >= 103:
        # SPDM 1.3+ has a "context" field at the end
        request_len += 8
    if signature_found:
        # Signature requested; contains a nonce
        request_len += 32
        request_nonce = data[offset + 4:offset + 36]
        if version_num >= 101:
            # SPDM 1.1+ has a "slot ID param" field if a signature is requested
            request_len += 1
    offset += request_len

    # MEASUREMENTS response
    # Check the response code is correct
    if data[offset + 1] != 0x60:  # MEASUREMENTS
        raise RedfishInvalidSignedMeasurements("Invalid MEASUREMENTS response code: 0x{:02X}".format(data[offset + 1]))
    response_length = 42
    if version_num >= 103:
        # SPDM 1.3+ has a "context" field before the signature
        response_length += 8
    # Add in the record length and opaque data length
    record_length = int.from_bytes(data[offset + 5:offset + 8], byteorder="little")
    opaque_len = int.from_bytes(data[offset + record_length + 40:offset + record_length + 42], byteorder="little")
    response_length += record_length + opaque_len
    # Pull out the different measurement blocks
    measurement_block_off = offset + 8
    for i in range(0, data[offset + 4]):
        block_length = int.from_bytes(data[measurement_block_off + 2:measurement_block_off + 4], byteorder="little")
        block_data = { "Index": data[measurement_block_off], "MeasurementSpecification": data[measurement_block_off + 1], "Measurement": data[measurement_block_off + 4:measurement_block_off + 4 + block_length] }
        measurements.append(block_data)
        measurement_block_off += 4 + block_length
    offset += response_length

    # If there's a signature, advance past it
    if signature_found:
        offset += signature_len

    return offset, signature_found, request_nonce
