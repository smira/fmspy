# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Time service.
"""

import time

def seconds():
    """
    Current time in seconds (UTC).
    """
    return int(time.time())

def milliseconds():
    """
    Current time in milliseconds (UTC).
    """
    return int(time.time() * 1000)

