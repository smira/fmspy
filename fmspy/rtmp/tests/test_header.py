# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.rtmp.header}.
"""

import unittest
import copy

from pyamf.util import BufferedByteStream

from fmspy.rtmp.header import RTMPHeader, NeedBytes

class RTMPHeaderTestCase(unittest.TestCase):
    """
    Test case for L{fmspy.rtmp.header.RTMPHeader}.
    """

    data = [ 
        ( 
             "\x03\x00\x00\x01\x00\x01\x05\x14\x00\x00\x00\x00", 
             RTMPHeader(3, 1, 261, 0x14, 0),
             None
        ),
        ( 
             "\x02\x00\x00\x01\x00\x01\x05\x14\x00\x00\x00\x00", 
             RTMPHeader(2, 1, 261, 0x14, 0),
             None
        ),
        (
             "\xc3",
             RTMPHeader(3, None, None, None, None),
             RTMPHeader(3, 1, 261, 0x14, 0),
        ),            
        (
             "\x83\x00\x00\x01",
             RTMPHeader(3, 1, None, None, None),
             RTMPHeader(3, 2, 261, 0x14, 0),
        ),
        (
             "\x43\x00\x00\x01\x00\x01\x05\x14",
             RTMPHeader(3, 1, 261, 0x14, None),
             RTMPHeader(3, 1, 261, 0x15, 0),
        )            
    ]    

    def setUp(self):
        self.h1 = RTMPHeader(3, 1, 261, 0x14, 0)
        self.h2 = RTMPHeader(2, 1, 261, 0x14, 0)
        self.h3 = RTMPHeader(3, 1, 261, 0x14, 0)

    def test_eq(self):
        self.failUnlessEqual(self.h1, self.h3)
        self.failIfEqual(self.h1, self.h2)

    def test_repr(self):
        self.failUnlessEqual("<RTMPHeader(object_id=3, timestamp=1, length=261, type=0x14, stream_id=0)>", repr(self.h1))

    def test_read(self):
        for fixture in self.data:
            self.failUnlessEqual(fixture[1], RTMPHeader.read(BufferedByteStream(fixture[0])))

    def test_read_short(self):
        for fixture in self.data:
            for l in xrange(len(fixture[0])-1):
                try:
                    RTMPHeader.read(BufferedByteStream(fixture[0][0:l]))
                    self.fail()
                except NeedBytes, (bytes,):
                    self.failUnlessEqual(len(fixture[0])-l if l != 0 else 1, bytes)

    def test_fill(self):
        f = RTMPHeader(6, 7, 8, 9, 10)
        h = RTMPHeader(1, 2, 3, 4, 5)
        h.fill(f)
        self.assertEqual(RTMPHeader(1, 2, 3, 4, 5), h)

        h = RTMPHeader(1, 2, 3, 4, None)
        h.fill(f)
        self.assertEqual(RTMPHeader(1, 2, 3, 4, 10), h)

        h = RTMPHeader(1, 2, 3, None, None)
        h.fill(f)
        self.assertEqual(RTMPHeader(1, 2, 3, 9, 10), h)

        h = RTMPHeader(1, 2, None, None, None)
        h.fill(f)
        self.assertEqual(RTMPHeader(1, 2, 8, 9, 10), h)

        h = RTMPHeader(1, None, None, None, None)
        h.fill(f)
        self.assertEqual(RTMPHeader(1, 7, 8, 9, 10), h)

        h = RTMPHeader(None, None, None, None, None)
        self.failUnlessRaises(AssertionError, h.fill, f)

        h = RTMPHeader(1, 2, 3, 4, None)
        f = RTMPHeader(6, 7, 8, 9, None)
        self.failUnlessRaises(AssertionError, h.fill, f)

    def test_diff(self):
        self.failUnlessEqual(0, self.h1.diff(self.h1))
        self.failUnlessEqual(0, self.h1.diff(self.h3))
        self.failUnlessRaises(AssertionError, self.h1.diff, self.h2)

        self.failUnlessEqual(1, self.h1.diff(RTMPHeader(3, 444, 261, 0x14, 0)))
        self.failUnlessEqual(2, self.h1.diff(RTMPHeader(3, 1, 262, 0x14, 0)))
        self.failUnlessEqual(2, self.h1.diff(RTMPHeader(3, 1, 261, 0x15, 0)))
        self.failUnlessEqual(3, self.h1.diff(RTMPHeader(3, 1, 261, 0x14, 11)))

    def test_write(self):
        for fixture in self.data:
            h = copy.copy(fixture[1])
            h.fill(self.h1)

            self.failUnlessEqual(fixture[0], h.write(previous=fixture[2]))

