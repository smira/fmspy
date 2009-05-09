# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.application.application}.
"""

from twisted.trial import unittest

from fmspy.application.application import Application
from fmspy.config import config

class TestApplication(Application):
    """
    Test application.
    """

class ApplicationTestCase(unittest.TestCase):
    """
    Testcase for L{fmspy.application.application.Application}.
    """

    def setUp(self):
        self.a = TestApplication()

    def test_name(self):
        self.failUnlessEqual('TestApplication', self.a.name())

    def test_enabled(self):
        self.failIf(self.a.enabled())
        config.add_section('TestApplication')
        config.set('TestApplication', 'enabled', 'yes')
        try:
            self.failUnless(self.a.enabled())
        finally:
            config.remove_option('TestApplication', 'enabled')
            config.remove_section('TestApplication')

    def test_repr(self):
        self.failUnlessEqual("<TestApplication>", repr(self.a))
