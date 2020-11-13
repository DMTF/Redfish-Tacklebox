#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

from setuptools import setup
from codecs import open

with open( "README.md", "r", "utf-8" ) as f:
    long_description = f.read()

setup(
    name = "redfish_utilities",
    version = "1.1.1",
    description = "Redfish Utilities",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "DMTF, https://www.dmtf.org/standards/feedback",
    license = "BSD 3-clause \"New\" or \"Revised License\"",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Communications"
    ],
    keywords = "Redfish",
    url = "https://github.com/DMTF/Redfish-Tacklebox",
    packages = [ "redfish_utilities" ],
    scripts = [
        "scripts/rf_accounts.py",
        "scripts/rf_bios_settings.py",
        "scripts/rf_boot_override.py",
        "scripts/rf_discover.py",
        "scripts/rf_event_service.py",
        "scripts/rf_logs.py",
        "scripts/rf_power_reset.py",
        "scripts/rf_sensor_list.py",
        "scripts/rf_sys_inventory.py",
        "scripts/rf_update.py"
    ],
    install_requires = [ "redfish" ]
)
