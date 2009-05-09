# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Example echo application.
"""

from zope.interface import implements
from twisted.plugin import IPlugin

from fmspy.application import Application

class EchoApplication(Application):
    """
    Example application: echo.

    Echo application sends back what it receives.
    """
    implements(IPlugin)

app = EchoApplication()
