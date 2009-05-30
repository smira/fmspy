# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Configuration file handling.
"""

import ConfigParser

config = ConfigParser.SafeConfigParser()
config_files = []

try:
    from pkg_resources import Requirement, resource_filename, DistributionNotFound

    try:
        config_files.append(resource_filename(Requirement.parse("fmspy"), "etc/fmspy.cfg"))
    except DistributionNotFound:
        pass

except ImportError:
    pass 

config_files.extend(['/etc/fmspy.cfg', '/ust/local/etc/fmspy.cfg', 'fmspy.cfg'])

config.read(config_files)

