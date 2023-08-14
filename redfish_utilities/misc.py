#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Miscellaneous

File : misc.py

Brief : Miscellaneous functions with common script logic
"""

import sys

def logout( context, ignore_error = False ):
    """
    Performs a logout of the service and allows for exceptions to be ignored

    Args:
        context: The Redfish client object with an open session
        ignore_error: Indicates if exceptions during logout are ignored
    """

    if context is not None:
        try:
            context.logout()
        except Exception as e:
            if ignore_error:
                pass
            else:
                raise
    return

def print_password_change_required_and_logout( context, args ):
    """
    Common help text when handling password change required conditions

    Args:
        context: The Redfish client object with an open session
        args: The argparse object from the calling script
    """

    print( "Password change required.  To set a new password, run the following:" )
    print( "rf_accounts.py -r {} -u {} -p <old password> --setpassword {} <new password>".format( args.rhost, args.user, args.user ) )
    logout( context, ignore_error = True )  # Some services do not allow session logout in this condition
    return
