# Raw Request (rf_raw_request.py)

Copyright 2019-2025 DMTF.  All rights reserved.

## About

A tool perform a raw request to a Redfish service.

## Usage

```
usage: rf_raw_request.py [-h] --user USER --password PASSWORD --rhost RHOST
                         [--method {GET,HEAD,POST,PATCH,PUT,DELETE}] --request
                         REQUEST [--body BODY] [--verbose]

A tool perform a raw request to a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)
  --request REQUEST, -req REQUEST
                        The URI for the request

optional arguments:
  -h, --help            show this help message and exit
  --method {GET,HEAD,POST,PATCH,PUT,DELETE}, -m {GET,HEAD,POST,PATCH,PUT,DELETE}
                        The HTTP method to perform; performs GET if not
                        specified
  --body BODY, -b BODY  The body to provide with the request; can be a JSON
                        string for a JSON request, a filename to send binary
                        data, or an unstructured string
  --verbose, -v         Indicates if HTTP response codes and headers are
                        displayed
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then perform the requested method on the specified URI with an optional body, specified by the *method*, *request*, and *body* arguments.
It will then display the response of the operation from the service.

Example; GET operation:

```
$ rf_raw_request.py -u root -p root -r https://192.168.1.100 -req /redfish/v1/SessionService
{
    "@odata.id": "/redfish/v1/SessionService",
    "@odata.type": "#SessionService.v1_1_8.SessionService",
    "Description": "Session Service",
    "Id": "SessionService",
    "Name": "Session Service",
    "ServiceEnabled": true,
    "SessionTimeout": 30,
    "Sessions": {
        "@odata.id": "/redfish/v1/SessionService/Sessions"
    },
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}
```

Example; PATCH operation:

```
$ rf_raw_request.py -u root -p root -r https://192.168.1.100 -req /redfish/v1/Systems/1 -m PATCH -b '{"AssetTag": "New tag"}'
No response body
```
