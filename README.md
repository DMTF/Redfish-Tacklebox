# Redfish Tacklebox

Copyright 2019-2024 DMTF.  All rights reserved.

## About

Redfish Tacklebox contains a set of Python3 utilities to perform common management operations with a Redfish service.
The utilities can be used as part of larger management applications, or be used as standalone command line tools.

## Installation

`pip install redfish_utilities`

### Building from Source

```
python setup.py sdist
pip install dist/redfish_utilities-x.x.x.tar.gz
```

### Building Docker

* Pull the container from Docker Hub:

    ```bash
    docker pull dmtf/redfish-utilities:latest
    ```
* Build a container from local source:

    ```bash
    docker build -t dmtf/redfish-utilities:latest .
    ```
* Build a container from GitHub:

    ```bash
    docker build -t dmtf/redfish-utilities:latest https://github.com/DMTF/Redfish-Tacklebox.git
    ```

## Requirements

External modules:
* redfish: https://pypi.python.org/pypi/redfish
* XlsxWriter: https://pypi.org/project/XlsxWriter

You may install the external modules by running:

`pip install -r requirements.txt`

## Utilities

* [Discover (rf_discover.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_discover.md)
* [Sensor List (rf_sensor_list.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_sensor_list.md)
* [System Inventory (rf_sys_inventory.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_sys_inventory.md)
* [Logs (rf_logs.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_logs.md)
* [Power/Reset (rf_power_reset.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_power_reset.md)
* [Boot Override (rf_boot_override.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_boot_override.md)
* [Virtual Media (rf_virtual_media.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_virtual_media.md)
* [BIOS Settings (rf_bios_settings.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_bios_settings.md)
* [Manager Configuration (rf_manager_config.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_manager_config.md)
* [Accounts (rf_accounts.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_accounts.md)
* [Update (rf_update.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_update.md)
* [Event Service (rf_event_service.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_event_service.md)
* [Licenses (rf_licenses.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_licenses.md)
* [Certificates (rf_certificates.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_certificates.md)
* [Diagnostic Data (rf_diagnostic_data.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_diagnostic_data.md)
* [Assembly (rf_assembly.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_assembly.md)
* [Power Equipment (rf_power_equipment.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_power_equipment.md)
* [Raw Request (rf_raw_request.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_raw_request.md)
* [Test Event Listener (rf_test_event_listener.py)](https://github.com/DMTF/Redfish-Tacklebox/blob/main/docs/rf_test_event_listener.md)

## Release Process

1. Go to the "Actions" page
2. Select the "Release and Publish" workflow
3. Click "Run workflow"
4. Fill out the form
5. Click "Run workflow"
