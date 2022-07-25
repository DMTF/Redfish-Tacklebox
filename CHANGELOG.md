# Change Log

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
