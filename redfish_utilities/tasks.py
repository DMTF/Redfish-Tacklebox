#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2025 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Tasks Module

File : tasks.py

Brief : This file contains the definitions and functionalities for interacting
        with Tasks for a given Redfish service
"""

import sys
import time


def poll_task_monitor(context, response, silent=False):
    """
    Monitors a task monitor until it's complete and prints out progress
    NOTE: This call will block until the task is complete

    Args:
        context: The Redfish client object with an open session
        response: The initial response from the operation that produced the task
        silent: Indicates if the task progress is to be hidden

    Returns:
        The final response of the request
    """

    # No task was produced; just return the existing response
    if not response.is_processing:
        return response

    # Poll the task until completion
    task_monitor = response
    while task_monitor.is_processing:
        # Print the progress
        if silent is False:
            task_state = None
            task_percent = None
            try:
                task_state = task_monitor.dict.get("TaskState", None)
                task_percent = task_monitor.dict.get("PercentComplete", None)
            except Exception:
                # 202 responses are allowed to not have a response body
                pass
            if task_state is None:
                task_state = "Running"
            if task_percent is None:
                progress_str = "Task is {}\r".format(task_state)
            else:
                progress_str = "Task is {}: {}% complete\r".format(task_state, task_percent)
            sys.stdout.write("\x1b[2K")
            sys.stdout.write(progress_str)
            sys.stdout.flush()

        # Sleep for the requested time
        retry_time = response.retry_after
        if retry_time is None:
            retry_time = 1
        time.sleep(retry_time)

        # Check the monitor for an update
        task_monitor = response.monitor(context)
    if silent is False:
        sys.stdout.write("\x1b[2K")
        print("Task is Done!")

    return task_monitor
