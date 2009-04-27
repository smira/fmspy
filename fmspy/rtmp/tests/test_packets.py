# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.rtmp.packets}.
"""

import unittest

from fmspy.rtmp.header import RTMPHeader
from fmspy.rtmp.packets import Packet, DataPacket

class DataPacketTestCase(unittest.TestCase):
    """
    Test case for L{fmspy.rtmp.packets.DataPacket}.
    """

    def setUp(self):
        self.p1 = DataPacket(RTMPHeader(3, 1, 0, 0x14, 0), "aaaa")
        self.p2 = DataPacket(RTMPHeader(2, 1, 0, 0x14, 0), "dddddd")
        self.p3 = DataPacket(RTMPHeader(3, 1, 0, 0x14, 0), "aaaa")

    def test_eq(self):
        self.failUnlessEqual(self.p1, self.p3)
        self.failIfEqual(self.p1, self.p2)

    def test_repr(self):
        self.failUnlessEqual("<DataPacket(header=<RTMPHeader(object_id=3, timestamp=1, length=4, type=0x14, stream_id=0)>, data='aaaa')>", repr(self.p1))

