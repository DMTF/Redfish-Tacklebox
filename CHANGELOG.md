# Change Log

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
