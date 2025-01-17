# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md
FROM python:3.12.0-alpine

WORKDIR /src
COPY . /src/
RUN python3 -m pip install --no-cache-dir /src
