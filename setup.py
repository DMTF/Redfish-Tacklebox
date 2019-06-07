#! /usr/bin/python
# Copyright Notice:
# Copyright 2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

from setuptools import setup
from codecs import open

with open( "README.md", "r", "utf-8" ) as f:
    long_description = f.read()

setup(
    name = "redfish_utilities",
    version = "0.7.0",
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
    scripts = [ "scripts/rf_sensor_list", "scripts/rf_update" ],
    install_requires = [ "redfish" ]
)
