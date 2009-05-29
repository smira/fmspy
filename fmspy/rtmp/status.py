# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Status objects - used to send errors and other info to client.
"""

from twisted.python import failure

class Status(object):
    """
    Status objects are sent as 
    Invoke error results, for example.

    @ivar code: error code (in NetConnection hierarchy)
    @type code: C{str}
    @ivar level: error level (status/error)
    @type level: C{str}
    @ivar description: error description (custom)
    @type description: C{str}
    """

    def __init__(self, code="NetConnection.Error", level="error", description="", **kwargs):
        """
        Constructor.

        @param code: error code (in NetConnection hierarchy)
        @type code: C{str}
        @param level: error level (status/error)
        @type level: C{str}
        @param description: error description (custom)
        @type description: C{str}
        """
        self.code = code
        self.level = level
        self.description = description
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "Status(code=%r, level=%r, description=%r)" % (self.code, self.level, self.description)

    @staticmethod
    def from_failure(fail):
        """
        Build status object from failure.

        @param fail: failure or exception
        @type fail: C{Failure}
        """
        if isinstance(fail, failure.Failure):
            fail = fail.value
        
        kwargs = { 'description' : repr(fail) }

        if hasattr(fail, 'code'):
            kwargs['code'] = fail.code

        return Status(**kwargs)
