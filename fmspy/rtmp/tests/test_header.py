# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.rtmp.header}.
"""

import unittest

from fmspy.rtmp.header import RTMPHeader

class RTMPHeaderTestCase(unittest.TestCase):
    """
    Test case for L{fmspy.rtmp.header.RTMPHeader}.
    """

    def setUp(self):
        self.h1 = RTMPHeader(3, 1, 261, 0x14, 0)
        self.h2 = RTMPHeader(2, 1, 261, 0x14, 0)
        self.h3 = RTMPHeader(3, 1, 261, 0x14, 0)

    def test_eq(self):
        self.failUnlessEqual(self.h1, self.h3)
        self.failIfEqual(self.h1, self.h2)

    def test_repr(self):
        self.failUnlessEqual("<RTMPHeader(object_id=3, timestamp=1, length=261, type=0x14, stream_id=0>", repr(self.h1))

