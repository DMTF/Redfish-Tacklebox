# Component Integrity (rf_component_integrity.py)

Copyright 2019-2026 DMTF.  All rights reserved.

## About

A tool to manage component integrity on a Redfish service.

## Usage

```
usage: rf_component_integrity.py [-h] --user USER --password PASSWORD --rhost
                                 RHOST [--debug] {list,getsignedmeasurements}
                                 ...

A tool to manage component integrity on a Redfish service

positional arguments:
  {list,getsignedmeasurements}
    list                Displays a list of component integrity instances
    getsignedmeasurements
                        Gets signed measurements for a component integrity
                        instance

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --debug               Creates debug file showing HTTP traces and exceptions
```

### List

Displays a list of component integrity instances.

```
usage: rf_component_integrity.py list [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then find all members in the component integrity collection and print summary details for each instance.

Example:

```
$ rf_component_integrity.py -u root -p root -r https://192.168.1.100 list
  Id               | Details
  SS-SPDM-0        | CPU1 RoT
                   | Component: /redfish/v1/Chassis/1U/TrustedComponents/AC-RoT0
                   | Type: SPDM; State: Enabled/OK
  SS-SPDM-1        | CPU1
                   | Component: /redfish/v1/Systems/437XR1138R2/Processors/CPU1
                   | Type: SPDM; State: Enabled/OK
  TPM-0            | System TPM
                   | Component: /redfish/v1/Chassis/1U/TrustedComponents/TPM
                   | Type: TPM; State: Enabled/OK
  USB-Integrity    | USB Controller 1
                   | Component: /redfish/v1/Systems/437XR1138R2/USBControllers/USB1
                   | Type: SPDM; State: Disabled/OK
```

### Get Signed Measurements

Gets signed measurements for a component integrity instance.

```
usage: rf_component_integrity.py getsignedmeasurements [-h]
                                                       --componentintegrity
                                                       COMPONENTINTEGRITY
                                                       [--verify]

required arguments:
  --componentintegrity COMPONENTINTEGRITY, -ci COMPONENTINTEGRITY
                        The identifier of the component integrity instance to
                        collect

optional arguments:
  -h, --help            show this help message and exit
  --verify, -v          Indicates if the signed measurements should be
                        verified
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then call the `SPDMGetSignedMeasurements` action for the specified component integrity instance, poll the task monitor for completion, parse the response payload, and print the parsed signed measurements.

* If *verify* is specified, it will also verify the signed measurements before printing them by performing the following:
    * Checks the nonce found in the signed measurement log matches the nonce sent in the request
    * Finds the certificate chain used to sign the measurements
    * Verifies the certificate chain is signed properly
    * Locates the public key of the device from the certificate chain
    * Verifies the signature over the measurements with the found public key

Example:

```
$ rf_component_integrity.py -u root -p root -r https://192.168.1.100 getsignedmeasurements -ci SS-SPDM-0 --verify
Signed Measurements:
  Type: SPDM
  SPDM Version: 1.2
  Signing Algorithm: TPM_ALG_ECDSA_ECC_NIST_P384
  Hashing Algorithm: TPM_ALG_SHA_384

  Supported Versions: 1.2.0
  Requester Size Limits: Max Transfer Size: 4096, Max Message Size: 4096
  Responder Size Limits: Max Transfer Size: 4096, Max Message Size: 4096

  Measurements:
    Index: 1, Specification: 01
    Data: d00f...
```
