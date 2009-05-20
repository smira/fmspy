# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Configuration file handling.
"""

import ConfigParser

config = ConfigParser.SafeConfigParser()
config_files = ['/etc/fmspy.cfg', '/ust/local/etc/fmspy.cfg', 'fmspy.cfg']

try:
    from pkg_resources import Requirement, resource_filename, DistributionNotFound

    try:
        config_files.append(resource_filename(Requirement.parse("spamfighter"), "etc/fmspy.cfg"))
    except DistributionNotFound:
        pass

except ImportError:
    pass 

config.read(config_files)

