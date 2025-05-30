#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Configuration Settings

File : config.py

Brief : This file contains configuration settings for the module; useful for
        debugging issues encountered on live systems or configuring global
        options.
"""

# Leverage known workarounds for non-conformant services, such as bypassing
# unexpected 4XX responses, missing properties, and malformed URIs
__workarounds__ = False

# Automate task handling for POST/PATCH/PUT/DELETE operations that should
# always be "fast"
__auto_task_handling__ = False
