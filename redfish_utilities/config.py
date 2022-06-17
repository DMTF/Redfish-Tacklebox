#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/master/LICENSE.md

"""
Configuration Settings

File : config.py

Brief : This file contains configuration settings for the module; useful for
        debugging issues encountered on live systems
"""

# Leverage known workarounds for non-conformant services, such as bypassing
# unexpected 4XX responses, missing properties, and malformed URIs
__workarounds__ = False
