# Certificates (rf_certificates.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage certificates on a Redfish service.

## Usage


```
usage: rf_certificates.py [-h] --user USER --password PASSWORD --rhost RHOST
                          [--debug]
                          {info,csrinfo,csr,install,delete} ...

A tool to manage certificates on a Redfish service

positional arguments:
  {info,csrinfo,csr,install,delete}
    info                Displays information about the certificates installed
                        on the service
    csrinfo             Displays information about options supported for
                        generating certificate signing requests
    csr                 Generates a certificate signing request
    install             Installs a certificate on the service
    delete              Deletes a certificate on the service

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

### Info

Displays information about the certificates installed on the service.

```
usage: rf_certificates.py info [-h] [--details]

optional arguments:
  -h, --help           show this help message and exit
  --details, -details  Indicates if the full details of each certificate
                       should be shown
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the certificate service, find its certificate locations, and display the certificates.

Example:

```
$ rf_certificates.py -u root -p root -r https://192.168.1.100 info
Certificate: /redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1
  Subject: CN=manager.contoso.org, O=Contoso, OU=ABC, C=US, ST=Oregon, L=Portland
  Issuer: CN=manager.contoso.org, O=Contoso, OU=ABC, C=US, ST=Oregon, L=Portland
  Valid Not Before: 2018-09-07T13:22:05Z, Valid Not After: 2019-09-07T13:22:05Z

Certificate: /redfish/v1/UpdateService/ClientCertificates/1
  Subject: CN=manager.contoso.org, O=Contoso, OU=ABC, C=US, ST=Oregon, L=Portland
  Issuer: CN=manager.contoso.org, O=Contoso, OU=ABC, C=US, ST=Oregon, L=Portland
  Valid Not Before: 2018-09-07T13:22:05Z, Valid Not After: 2019-09-07T13:22:05Z

Certificate: /redfish/v1/Systems/437XR1138R2/VirtualMedia/CD1/Certificates/1
  Subject: CN=redfish.dmtf.org, O=Contoso, OU=Image Hosting, C=US, ST=Oregon, L=Portland
  Issuer: CN=redfish.dmtf.org, O=Contoso, OU=Image Hosting, C=US, ST=Oregon, L=Portland
  Valid Not Before: 2021-09-22T20:50:08Z, Valid Not After: 2022-09-22T20:50:08Z

```

### Certificate Signing Request Info

Displays information about options supported for generating certificate signing requests.

```
usage: rf_certificates.py csrinfo [-h]

optional arguments:
  -h, --help  show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the certificate service, find the `GenerateCSR` action, and display the information obtained from its action info.

Example:

```
$ rf_certificates.py -u root -p root -r https://192.168.1.100 csrinfo
Generate CSR parameters:
  CommonName (required)
  AlternativeNames
  Organization (required)
  OrganizationalUnit (required)
  City (required)
  State (required)
  Country (required)
  Email
  KeyPairAlgorithm (required): TPM_ALG_RSA, TPM_ALG_ECDSA
  KeyBitLength
  KeyCurveId: TPM_ECC_NIST_P256, TPM_ECC_NIST_P384, TPM_ECC_NIST_P521
  CertificateCollection (required)
  KeyUsage: DigitalSignature, NonRepudiation, KeyEncipherment, DataEncipherment, KeyAgreement, KeyCertSign, CRLSigning, EncipherOnly, DecipherOnly, ServerAuthentication, ClientAuthentication, CodeSigning, EmailProtection, OCSPSigning
```

### Certificate Signing Request

Generates a certificate signing request.

```
usage: rf_certificates.py csr [-h] --certificatecollection
                              CERTIFICATECOLLECTION --commonname COMMONNAME
                              --organization ORGANIZATION --organizationalunit
                              ORGANIZATIONALUNIT --city CITY --state STATE
                              --country COUNTRY [--email EMAIL]
                              [--keyalg KEYALG] [--keylen KEYLEN]
                              [--keycurve KEYCURVE] [--out OUT]

required arguments:
  --certificatecollection CERTIFICATECOLLECTION, -col CERTIFICATECOLLECTION
                        The URI of the certificate collection where the signed
                        certificate will be installed
  --commonname COMMONNAME, -cn COMMONNAME
                        The common name of the component to secure
  --organization ORGANIZATION, -o ORGANIZATION
                        The name of the unit in the organization making the
                        request
  --organizationalunit ORGANIZATIONALUNIT, -ou ORGANIZATIONALUNIT
                        The name of the unit in the organization making the
                        request
  --city CITY, -l CITY  The city or locality of the organization making the
                        request
  --state STATE, -st STATE
                        The state, province, or region of the organization
                        making the request
  --country COUNTRY, -c COUNTRY
                        The two-letter country code of the organization making
                        the request

optional arguments:
  -h, --help            show this help message and exit
  --email EMAIL, -email EMAIL
                        The email address of the contact within the
                        organization making the request
  --keyalg KEYALG, -alg KEYALG
                        The type of key-pair for use with signing algorithms
  --keylen KEYLEN, -len KEYLEN
                        The length of the key, in bits, if the key pair
                        algorithm supports key size
  --keycurve KEYCURVE, -curve KEYCURVE
                        The curve ID to use with the key if the key pair
                        algorithm supports curves
  --out OUT, -out OUT   The file, with optional path, to save the certificate
                        signing request
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then locate the certificate service, find the `GenerateCSR` action, invoke the `GenerateCSR` action with the provided arguments, and display the certificate signing request produced by the service.

Example:

```
$ rf_certificates.py -u root -p root -r https://192.168.1.100 csr -col /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates -cn "manager.contoso.org" -o "Contoso" -ou "Contoso HW Div" -l "Portland" -st "Oregon" -c "US"
Generating cerficiate signing request...

-----BEGIN CERTIFICATE REQUEST-----
MIIC6DCCAdACAQAwejELMAkGA1UEBhMCVVMxDzANBgNVBAgMBk9yZWdvbjERMA8G
A1UEBwwIUG9ydGxhbmQxEDAOBgNVBAoMB0NvbnRvc28xFzAVBgNVBAsMDkNvbnRv
c28gSFcgRGl2MRwwGgYDVQQDDBNtYW5hZ2VyLmNvbnRvc28ub3JnMIIBIjANBgkq
hkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA47GGZhtpNwpG4wPhX8swSL+LkvHqUPP1
94zmIJNGKRYa3GoxfrStKMFqlUG6o/dR95YZi0LEp0gFJy89ac3qEC6A/WPC5Ug7
0EPWam46H5Qc/JtuwI7gycaHe6Pt6l2gShR/EMTI5iM7+mJkREYrVa8NLQ5+jHdn
aNJWxyRThPtyu66Ib+X4RkwWck68CYKCg196t5ISYgmSyE/4uSEGdzH+3P9q/8oO
91xpP83uEPfAICMKU706+mFgDjQx4seNldLVu+jLszzpRAxHpMPhVFAgUgiAyxe4
BWZ9YQCp5cVZr+a6xqqVBhznSmFiHOXKx4Q3d0OGMlQLmcDwbdCCnwIDAQABoCkw
JwYJKoZIhvcNAQkOMRowGDAJBgNVHRMEAjAAMAsGA1UdDwQEAwIF4DANBgkqhkiG
9w0BAQsFAAOCAQEAA9jeax5q4Zs+/0BqCV1sVrsthJtf8SVAUyjJTNJQmkMP/c+h
+f8SrwJM8CeC+DZgIWyP1fDo8cBQSVQThzPyPr+olSI0nwsvS6g28BOenywI+J70
5QwXBs4nJciJQopk6vdBGbISAIcWepoEcaLFJD940KJJ3I6eWFdU93IXJsRAzmos
x2a1mt+whdDVwA6EA+Eu20qwfouJJ0TaZhXrCktf0HQrlqNQUJpfBJWoYvjFc2PI
nh9JMulAPdhiL93opXARljYTwwbxbQG92L5rC7A31pCp+/GMJ+qU87/1HarrrfUD
z0UFdFZT+w8+ohq/56UOcabzZroVoWZU0zzkrw==
-----END CERTIFICATE REQUEST-----


```

### Install

Installs a certificate on the service.

```
usage: rf_certificates.py install [-h] --destination DESTINATION --certificate
                                  CERTIFICATE [--key KEY]

required arguments:
  --destination DESTINATION, -dest DESTINATION
                        The installation URI of the certificate; either a
                        certificate collection to insert, or an existing
                        certificate to replace
  --certificate CERTIFICATE, -cert CERTIFICATE
                        The file, and optional path, of the certificate to
                        install

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -key KEY   The file, and optional path, of the private key for
                        the certificate to install
``` 

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then inspect the URI referenced by the *destination* argument.
If the *destination* is discovered to be a certificate collection, it will install the contents provided by the *certificate* and *key* arguments into the referenced collection.
Otherwise, it will locate the certificate service, find the `ReplaceCertificate` action, and invoke the action with the contents provided by the *certificate* and *key* arguments to replace the certificate referenced by the *destination* argument.

Example:

```
$ rf_licenses.py -u root -p root -r https://192.168.1.100 install --destination /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates/1 --cert /home/user/my_new_cert.pem
Installing /home/user/my_new_cert.pem...
```

### Delete

Deletes a certificate on the service.

```
usage: rf_certificates.py delete [-h] --certificate CERTIFICATE

required arguments:
  --certificate CERTIFICATE, -cert CERTIFICATE
                        The URI of the certificate to delete

optional arguments:
  -h, --help            show this help message and exit
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then delete the certificate referenced by the *certificate* argument.

Example:

```
$ rf_certificates.py -u root -p root -r https://192.168.1.100 delete --certificate /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates/1
Deleting /redfish/v1/Managers/1/NetworkProtocol/HTTPS/Certificates/1...
```
