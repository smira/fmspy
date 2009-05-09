# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Teat application plugin.
"""

from zope.interface import implements
from twisted.plugin import IPlugin

from fmspy.application import Application

class TestApplication(Application):
    """
    Test application.
    """
    implements(IPlugin)

    def load(self):
        self.loaded = True

app = TestApplication()
