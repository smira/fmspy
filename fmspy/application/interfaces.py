# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Application interfaces.
"""

from zope.interface import Interface

class IApplication(Interface):
    """
    Application interface.

    Application is customized behavior of FMSPy server. Every client
    connects to application, uses its methods, etc.
    """

    def name():
        """
        Get application name.

        @rtype: C{str}
        """

    def enabled():
        """
        Is application enabled or not?

        @rtype: C{bool}
        """

    def load():
        """
        Potentially Deferred action that is called
        on application being loaded.

        Deferred can delay server startup (for example, connecting
        to database).
        """

