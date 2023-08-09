#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
some misc function implment in here

File : misc.py

Brief : some misc function implment in here
"""
import sys
from redfish.rest.v1 import BadRequestError
def logout(redfish_obj, print_error = False):
    if redfish_obj is not None:
        try:
            redfish_obj.logout()
        except BadRequestError as e:
            pass
        except Exception as e:
            if print_error is True:
                print(e)
    return

def print_password_change_required_and_logout(redfish_obj, args):
    print("Password change required\n run rf_accounts.py -r {} -u {} -p <old password> --setpassword {} <new password> \nto set your password\n".format(args.rhost ,args.user, args.user))
    logout(redfish_obj, print_error = True)
    return
