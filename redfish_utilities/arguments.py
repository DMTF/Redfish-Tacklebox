import argparse


def validate_auth(args):
    if (args.user and args.password and not args.session_token) or (
        args.session_token and not (args.user or args.password)
    ):
        return
    else:
        print("You must specify both --user and --password or --session-token")
        quit(1)


def create_parent_parser(description: str = "", auth: bool = False, rhost: bool = False):
    parent_parser = argparse.ArgumentParser(description=description, add_help=False)

    parent_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Creates debug file showing HTTP traces and exceptions",
    )
    parent_parser.add_argument("--log-to-console", action="store_true", help="Enable logging to console")
    parent_parser.add_argument("--log-to-file", action="store_true", help="Enable logging to a file")
    parent_parser.add_argument(
        "--debug", action="store_true", help="Creates debug file showing HTTP traces and exceptions"
    )

    if auth:
        parent_parser.add_argument("--user", "-u", type=str, help="The user name for authentication")
        parent_parser.add_argument("--password", "-p", type=str, help="The password for authentication")
        parent_parser.add_argument("--session-token", "-t", type=str, help="The session token for authentication")

    if rhost:
        parent_parser.add_argument(
            "--rhost", "-r", type=str, required=True, help="The address of the Redfish service (with scheme)"
        )

    return parent_parser


def validate_args(args):
    validate_auth(args)
