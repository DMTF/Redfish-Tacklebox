#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

from setuptools import setup
from setuptools import Command as _Command
from codecs import open
import sys
import os

class Pyinstaller(_Command):
    description: 'Pyinstaller'
    user_options = []
    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)
        self.flags = ""
        self.scripts = []
        self.packages = []
        if not os.path.exists("./dist"):
            os.mkdir("dist")
        if not os.path.exists("./spec"):
            os.mkdir("spec")
    def initialize_options(self):
        self.flags = ""
        self.scripts = []
        self.packages = []

    def finalize_options(self):
        self.flags = "--specpath ./spec"
        self.scripts = self.distribution.scripts
        self.packages = self.distribution.packages
        for package in self.packages:
            self.flags = "{} --collect-all {}".format(self.flags,package)

    def pyinstaller(self, target):
        if os.system("pyinstaller --onefile {} {}".format(target, self.flags)):
            raise Exception("PyInstaller failed!")
    def run(self):
        for scripts in self.scripts:
            self.pyinstaller(scripts)

with open( "README.md", "r", "utf-8" ) as f:
    long_description = f.read()

setup(
    name = "redfish_utilities",
    version = "3.2.0",
    description = "Redfish Utilities",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "DMTF, https://www.dmtf.org/standards/feedback",
    license = "BSD 3-clause \"New\" or \"Revised License\"",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Topic :: Communications"
    ],
    keywords = "Redfish",
    url = "https://github.com/DMTF/Redfish-Tacklebox",
    packages = [ "redfish_utilities" ],
    scripts = [
        "scripts/rf_accounts.py",
        "scripts/rf_bios_settings.py",
        "scripts/rf_boot_override.py",
        "scripts/rf_certificates.py",
        "scripts/rf_diagnostic_data.py",
        "scripts/rf_discover.py",
        "scripts/rf_event_service.py",
        "scripts/rf_licenses.py",
        "scripts/rf_logs.py",
        "scripts/rf_manager_config.py",
        "scripts/rf_power_reset.py",
        "scripts/rf_raw_request.py",
        "scripts/rf_sensor_list.py",
        "scripts/rf_sys_inventory.py",
        "scripts/rf_update.py",
        "scripts/rf_virtual_media.py"
    ],
    install_requires = [ "redfish>=3.2.1", "XlsxWriter>=1.2.7" ],
    cmdclass={
        'pyinstaller': Pyinstaller
    }
)
