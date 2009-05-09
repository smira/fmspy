# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.application.factory}.
"""

from twisted.trial import unittest

from fmspy.application.factory import ApplicationFactory
import fmspy.application.tests
from fmspy.config import config

class ApplicationFactoryTestCase(unittest.TestCase):
    """
    Testcase for L{fmspy.application.factory.ApplicationFactory}.
    """
    
    def setUp(self):
        self.f = ApplicationFactory(fmspy.application.tests)

    def test_load(self):
        def check(_):
            self.failUnlessEqual({}, self.f.apps)
        return self.f.load_applications().addCallback(check)

    def test_load2(self):
        config.add_section('TestApplication')
        config.set('TestApplication', 'enabled', 'yes')
        config.set('TestApplication', 'name', 'test')

        def check(_):
            self.failUnlessEqual(['test'], self.f.apps.keys())
            self.failUnless(self.f.apps.values()[0].loaded)

        def cleanup(r):
            config.remove_option('TestApplication', 'enabled')
            config.remove_option('TestApplication', 'name')
            config.remove_section('TestApplication')

            return r

        return self.f.load_applications().addCallback(check).addBoth(cleanup)
