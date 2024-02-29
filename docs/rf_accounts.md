# Accounts (rf_accounts.py)

Copyright 2019-2024 DMTF.  All rights reserved.

## About

A tool to manage user accounts on a Redfish service.

## Usage

```
usage: rf_accounts.py [-h] --user USER --password PASSWORD --rhost RHOST
                      [--add name password role] [--delete DELETE]
                      [--setname old_name new_name]
                      [--setpassword name new_password]
                      [--setrole name new_role] [--enable ENABLE]
                      [--disable DISABLE] [--unlock UNLOCK] [--debug]

A tool to manage user accounts on a Redfish service

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The address of the Redfish service (with scheme)

optional arguments:
  -h, --help            show this help message and exit
  --add name password role, -add name password role
                        Adds a new user account
  --delete DELETE, -delete DELETE
                        Deletes a user account with the given name
  --setname old_name new_name, -setname old_name new_name
                        Sets a user account to a new name
  --setpassword name new_password, -setpassword name new_password
                        Sets a user account to a new password
  --setrole name new_role, -setrole name new_role
                        Sets a user account to a new role
  --enable ENABLE, -enable ENABLE
                        Enables a user account with the given name
  --disable DISABLE, -disable DISABLE
                        Disabled a user account with the given name
  --unlock UNLOCK, -unlock UNLOCK
                        Unlocks a user account with the given name
  --debug               Creates debug file showing HTTP traces and exceptions
```

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
Based on the parameters, it will display, add, delete, or modify user accounts.

* The *add* argument is used to create a new user account
* The *delete* argument is used to delete a user account based on the given user name
* The *setname* argument is used to change the name of a user account
* The *setpassword* argument is used to change the password of a user account
* The *setrole* argument is used to change the role of a user account
* The *enable* argument is used to enable a user account
* The *disable* argument is used to disable a user account
* The *unlock* argument is used to unlock a user account
* If none of the above arguments are given, a table of the user accounts is provided

Example; display existing user accounts:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100

  Name                 | Role                 | Locked     | Enabled   
  Administrator        | Administrator        | False      | True      

```

Example; add a new account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -add new_name new_password new_role
Adding new user 'new_name'
```

Example; delete an account:

```
$rf_accounts.py -u root -p root -r https://192.168.1.100 -delete user_to_delete
Deleting user 'user_to_delete'
```

Example; change the username for an account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -setname user_to_change new_name
Changing name of user 'user_to_change' to 'new_name'
```

Example; change the password for an account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -setpassword user_to_change new_password
Changing password of user 'user_to_change'
```

Example; change the role for an account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -setrole user_to_change Operator
Changing role of user 'user_to_change' to 'Operator'
```

Example; enable a user account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -enable user_to_change
Enabling user 'user_to_change'
```

Example; disable a user account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -disable user_to_change
Disabling user 'user_to_change'
```

Example; unlock a user account:

```
$ rf_accounts.py -u root -p root -r https://192.168.1.100 -unlock user_to_change
Unlocking user 'user_to_change'
```
