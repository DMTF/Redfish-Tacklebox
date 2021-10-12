#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Redfish BIOS Settings Info

File : rf_bios_settings_info.py

Brief : This script uses the redfish_utilities module to display BIOS settings information of a system
"""

import argparse
import redfish
import redfish_utilities

# Get the input arguments
argget = argparse.ArgumentParser(description="A tool to manager BIOS settings for a system")
argget.add_argument("--user", "-u", type=str, required=True, help="The user name for authentication")
argget.add_argument("--password", "-p", type=str, required=True, help="The password for authentication")
argget.add_argument("--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)")
argget.add_argument("--system", "-s", type=str, help="The ID of the system to manage (default = the only system)")
argget.add_argument("--language", "-l", type=str, help="The language of the BIOS setting to get (default = en-US)")
argget.add_argument("--attribute", "-a", type=str, nargs='*', help="The BIOS setting to get (default = all settings)")
args = argget.parse_args()

# Set up the Redfish object
redfish_obj = redfish.redfish_client(base_url=args.rhost, username=args.user, password=args.password)
redfish_obj.login(auth="session")

try:
    # Get the BIOS settings info
    bios_settings = redfish_utilities.get_system_bios_info(redfish_obj, args.system, args.language, args.attribute)
    element_to_display = ['AttributeName', 'HelpText', 'Type', 'CurrentValue', 'DefaultValue', 'Value',
                          'UpperBound', 'LowerBound', 'ScalarIncrement', 'MaxLength', 'MinLength']
    bios_line_format = '  {:16s} : {}'

    if not bios_settings:
        print('No attribute "{}" found'.format(', '.join(args.attribute)))
    for index, bios_setting in enumerate(bios_settings):
        print('-' * 30 + str(index) + '-' * 30)
        for element in element_to_display:
            if element not in list(bios_setting.keys()):
                continue
            # Special case for 'Value'
            if element == 'Value':
                value_to_display = []
                for setting in bios_setting[element]:
                    value_to_display.append(setting['ValueName'])
                print(bios_line_format.format('Value', ', '.join(value_to_display)))
                continue
            print(bios_line_format.format(element, bios_setting[element]))
        print('')
    print('Operation successes')
finally:
    # Log out
    redfish_obj.logout()
