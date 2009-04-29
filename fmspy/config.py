# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Configuration file handling.
"""

import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read(['fmspy.cfg'])

