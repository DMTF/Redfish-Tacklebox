# Change Log

## [3.4.1] - 2025-05-30
- Added new global config to automatically internalize task monitoring for select operations

## [3.4.0] - 2025-05-02
- Corrected the usage of the 'DateTimeLocalOffset' property when setting a manager's time

## [3.3.9] - 2025-04-21
- Fixed files to always be Unix format

## [3.3.8] - 2025-01-24
- Added 'rf_sel.py' script to simplify the ability for a user to find the SEL on a service

## [3.3.7] - 2025-01-17
- Added option to 'rf_bios_settings.py' to reset BIOS to the default settings
- Added 'rf_firmware_inventory.py' script to collect and display firmware versions

## [3.3.6] - 2024-10-25
- Added '--timeout' option to rf_update.py to manually specify a timeout for the file transfer

## [3.3.5] - 2024-09-27
- Corrected the regex pattern when trying to discover the local system's address when directly hosting firmware images

## [3.3.4] - 2024-08-09
- Fixed file handling for certificate installation
- Modified formatting of the sensor table from 'rf_sensor_list.py' to not truncate readings

## [3.3.3] - 2024-07-12
- Fixed 'list' commands for 'rf_power_equipment.py' and 'rf_thermal_equipment.py' to handle cases where properties are not supported or null

## [3.3.2] - 2024-06-14
- Added new 'rf_thermal_equipment.py' tool for managing thermal equipment, such as CDUs

## [3.3.1] - 2024-06-07
- Fixed change that was added for protecting from BrokenPipeError exceptions to not crash on Windows

## [3.3.0] - 2024-06-07
- Added handling for printing array properties with 'null' entries where allowed
- Removed truncation of log messages to fit the console screen in 'rf_logs.py'

## [3.2.9] - 2024-05-31
- Added protection from BrokenPipeError exceptions when piping rf_logs.py output

## [3.2.9] - 2024-05-31
- Added protection from BrokenPipeError exceptions when piping rf_logs.py output

## [3.2.8] - 2024-04-10
- Added missing check for presence of 'Sensors' when deciding which model to follow for collecting sensor info

## [3.2.7] - 2024-03-01
- Added 'rf_assembly.py' to manage Assembly resources on a service

## [3.2.6] - 2024-02-23
- Added 'rf_test_event_listener.py' tool to manually build event payloads

## [3.2.5] - 2024-02-09
- Added optional 'applytime' parameter to 'rf_update.py' to specify when to apply an update

## [3.2.4] - 2024-02-02
- Added 'rf_power_equipment.py' to collect data from rack PDUs and other power equipment

## [3.2.3] - 2024-01-19
- Minor changes to fix Python 3.12 warnings with usage of raw strings

## [3.2.2] - 2023-11-17
- Added new subcommands to 'rf_manager_config.py' to display and configure network protocol settings

## [3.2.1] - 2023-10-27
- Added PhysicalContext to rf_sensor_list.py

## [3.2.0] - 2023-09-15
- Added workaround flag to attempt to set boot override properties on settings resources for non-conformant implementations

## [3.1.9] - 2023-09-01
- Added 'rf_certificates.py' tool to manage certificates on a Redfish service

## [3.1.8] - 2023-08-14
- Added handling for password change required scenarios
- Updated 'rf_accounts.py' to directly modify a user's password when handling a password change required scenario
- Added options for controlling how 'rf_sensor_list.py' constructs sensor names
- Added timesouts and max retries to all requests
- Added dynamic scaling of the timeout of a multipart push update

## [3.1.7] - 2023-08-04
- Added ETag handling for PATCH and PUT operations in 'rf_raw_request.py'

## [3.1.6] - 2023-07-27
- Corrected excaption raising in several manager methods to properly reference the manager's identifier
- Added 'settime' command to 'rf_manager_config.py'

## [3.1.5] - 2023-07-07
- Added 'rf_licenses.py' tool to manage licenses on a Redfish service
- Added 'resettodefaults' subcommand to 'rf_manager_config.py'
- Updated 'setnet' in 'rf_manager_config.py' to allow for the 'Enabled' value for DHCPv6 control

## [3.1.4] - 2023-06-16
- Updated collection handling for systems, managers, and chassis to differentiate between HTTP 404 from other non-successful responses

## [3.1.3] - 2023-04-25
- Extended 'rf_raw_request.py' to allow it to send binary data from a file

## [3.1.2] - 2023-01-13
- Added support for multipart HTTP push updates

## [1.3.1] - 2022-12-02
- Corrected the usage of the 'workaround' flag in rf_bios_settings.py
- Added 'debug' argument to capture HTTP traces and exceptions to a log
- Enhanced system inventory logic to ensure properties are of the expected format instead of throwing an exception when malformed

## [1.3.0] - 2022-11-18
- Fixed bug where rf_raw_request.py would perform 'HEAD' instead of 'DELETE' when 'DELETE' is specified

## [1.2.9] - 2022-09-23
- Corrected passing of the event_types argument from rf_event_service.py when creating an event subscription

## [1.2.8] - 2022-08-12
- Corrected flow when handling system reset exceptions to ensure it stays raised

## [1.2.7] - 2022-08-05
- Corrected 'rf_sensor_list.py' to not assume all excerpts contain a reading
- Updated allowable reset types to include 'Suspend', 'Pause', and 'Resume'
- Updated error path for system reset requests to append reset types allowed by the system to the exception message

## [1.2.6] - 2022-07-25
- Added exception handling in each script to avoid printing full traces
- Minor documentation updates

## [1.2.5] - 2022-07-05
- Adding RPM packages to the build process

## [1.2.4] - 2022-06-17
- Enhancement added to fall back on using the Id property in Sensor for building the name if Name is not valid
- Moved usage of 'workarounds' flag to be a module-level flag rather than an individual parameter on each method

## [1.2.3] - 2022-03-18
- Added --mode argument to 'rf_boot_override.py' to control Legacy vs UEFI
- Added --info argument to 'rf_boot_override.py'

## [1.2.2] - 2022-03-10
- Corrected usage of the 'request' parameter in 'rf_raw_request.py'

## [1.2.1] - 2022-03-04
- Added 'rf_diagnostic_data.py' to collect diagnostic data from a log service
- Added power state reporting with the 'info' parameter in rf_power_reset.py

## [1.2.0] - 2022-02-11
- Fixed usage of 'EventTypes' when creating an event subscription

## [1.1.9] - 2022-01-14
- Added rf_raw_request.py for allowing a user to perform HTTP operations on a specified URI

## [1.1.8] - 2021-11-19
- Updated rf_sensor_list.py to support new power and thermal models

## [1.1.7] - 2021-10-04
- Added handling for lack of 'Destination' property in an event subscription when displaying the list of subscriptions
- Added support for legacy 'event types' subscriptions to enable usage with services that do not support newer methods of subscriptions

## [1.1.6] - 2021-08-30
- Added --workaround flag to rf_sys_inventory.py to attempt workaround logic for non-conformant services
- Added support for cataloging switches in rf_sys_inventory.py

## [1.1.5] - 2021-08-06
- Added --workaround flag to rf_bios_settings.py to attempt workaround logic for non-conformant services
- Added trailing slash checking in URI parsing of collections when extracting member identifiers

## [1.1.4] - 2021-05-14
- Added helper routines to collect identifiers for systems, managers, and Ethernet interfaces for managers
- Modified collection searching routines to leverage standardized URI patterns to minimize the number of transactions performed

## [1.1.3] - 2021-04-30
- Added rf_manager_config.py tool for configuring managers

## [1.1.2] - 2021-03-02
- Added rf_virtual_media.py tool for managing virtual media on a system

## [1.1.1] - 2020-11-13
- Added list of reset types to help text of rf_power_reset.py

## [1.1.0] - 2020-10-30
- Fixed usage of the --expand option in rf_event_service.py

## [1.0.9] - 2020-10-19
- Added rf_event_service.py tool for managing event subscriptions and displaying event service information

## [1.0.8] - 2020-07-10
- Added option to the inventory script to save information to a spreadsheet

## [1.0.7] - 2020-05-22
- Removed 'PushPowerButton' from simple reset list

## [1.0.6] - 2020-05-14
- Added rf_bios_settings.py utility for displaying and setting BIOS attributes
- Added enhancement to account deletion fallback routine to send two PATCH operations when clearing an account to ensure compatibility
- Added sensor state to the sensor objects constructed
- Enhanced construction of the PCIe device name being built to use other properties

## [1.0.5] - 2020-05-01
- Added enhancement to one time boot script to set the boot mode to Disabled when the target is selected to be None
- Added option in power/reset script to show available reset types
- Added enhancement to show valid Ids of resources when an exception is generated
- Fixed log script from hiding exceptions

## [1.0.4] - 2020-03-13
- Added rf_logs.py utility for reading and displaying logs

## [1.0.3] - 2020-01-17
- Added rf_discover.py utility to discover Redfish services via SSDP

## [1.0.2] - 2019-11-01
- Added support for using ETags for PATCHing ComputerSystem resources

## [1.0.1] - 2019-08-16
- Removed 'Account Lock' capability from rf_accounts
- Renamed all scripts to end in '.py' for Windows compatibility

## [1.0.0] - 2019-07-12
- Added rf_accounts utility to manage user accounts
- Made fix to handling of Storage Controllers in the inventory tool

## [0.9.0] - 2019-06-28
- Added rf_sys_inventory utility to scan a service and catalog system components

## [0.8.0] - 2019-06-21
- Added rf_boot_override utility to perform one time boot operations
- Added rf_power_reset utility to perform power/reset operations

## [0.7.0] - 2019-06-07
- Added local web server support for rf_update when a local file is specified

## [0.6.0] - 2019-05-31
- Added rf_update utility

## [0.5.0] - 2019-05-28
- Initial release
