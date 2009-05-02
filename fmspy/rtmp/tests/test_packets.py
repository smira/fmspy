# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.rtmp.packets}.
"""

import unittest

import pyamf
from pyamf.util import BufferedByteStream

from fmspy.rtmp.header import RTMPHeader
from fmspy.rtmp.packets import Packet, DataPacket, Invoke, BytesRead, Ping

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

class InvokeTestCase(unittest.TestCase):
    """
    Test case for L{fmspy.rtmp.packets.Invoke}.
    """

    data = [
            (
                { 'header' : RTMPHeader(object_id=3, timestamp=0, length=235, type=0x14, stream_id=0L),
                  'buf'    : BufferedByteStream('\x02\x00\x07connect\x00?\xf0\x00\x00\x00\x00\x00\x00\x03\x00\x03app\x02\x00\x04echo\x00\x08flashVer\x02\x00\rLNX 10,0,20,7\x00\x06swfUrl\x06\x00\x05tcUrl\x02\x00\x15rtmp://localhost/echo\x00\x04fpad\x01\x00\x00\x0ccapabilities\x00@.\x00\x00\x00\x00\x00\x00\x00\x0baudioCodecs\x00@\xa8\xee\x00\x00\x00\x00\x00\x00\x0bvideoCodecs\x00@o\x80\x00\x00\x00\x00\x00\x00\rvideoFunction\x00?\xf0\x00\x00\x00\x00\x00\x00\x00\x07pageUrl\x06\x00\x0eobjectEncoding\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t'),
                },
                Invoke(name=u'connect', argv=({'videoCodecs': 252, 'audioCodecs': 3191, 'flashVer': u'LNX 10,0,20,7', 'app': u'echo', 
                            'tcUrl': u'rtmp://localhost/echo', 'videoFunction': 1, 'capabilities': 15, 'pageUrl': pyamf.Undefined, 'fpad': False, 
                            'swfUrl': pyamf.Undefined, 'objectEncoding': 0},), id=1, header=RTMPHeader(object_id=3, timestamp=0, length=235, type=0x14, stream_id=0L)),
                False
            ),
            (
                { 'header' : RTMPHeader(object_id=3, timestamp=0, length=0, type=0x14, stream_id=0L),
                  'buf'    : BufferedByteStream('\x02\x00\x07destroy\x00@@\x80\x00\x00\x00\x00\x00\x03\x00\x0bvideoCodecs\x00@o\x80\x00\x00\x00\x00\x00\x00\x00\t'),
                },
                Invoke(name=u'destroy', argv=({'videoCodecs': 252},), id=33, header=RTMPHeader(object_id=3, timestamp=0, length=0, type=0x14, stream_id=0L)),
                True
            ),
           ]

    def test_eq(self):
        self.failUnlessEqual(Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=3)), Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=3)))
        self.failIfEqual(Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=3)), Invoke(name='b', argv=(), id=35.0, header=RTMPHeader(object_id=3)))
        self.failIfEqual(Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=3)), Invoke(name='a', argv=('a'), id=35.0, header=RTMPHeader(object_id=3)))
        self.failIfEqual(Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=3)), Invoke(name='a', argv=(), id=36.0, header=RTMPHeader(object_id=3)))
        self.failIfEqual(Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=3)), Invoke(name='a', argv=(), id=35.0, header=RTMPHeader(object_id=4)))

    def test_repr(self):
        self.failUnlessEqual("<Invoke(name=u'destroy', argv=({'videoCodecs': 252},), id=33, header=<RTMPHeader(object_id=3, timestamp=0, length=0, type=0x14, stream_id=0L)>)>", 
                repr(Invoke(name=u'destroy', argv=({'videoCodecs': 252},), id=33, header=RTMPHeader(object_id=3, timestamp=0, length=0, type=0x14, stream_id=0L))))

    def test_read(self):
        for fixture in self.data:
            fixture[0]['buf'].seek(0)
            self.failUnlessEqual(fixture[1], Invoke.read(**fixture[0]))

    def test_write(self):
        for fixture in self.data:
            if not fixture[2]:
                continue
            fixture[0]['buf'].seek(0)
            self.failUnlessEqual(fixture[0]['buf'].read(), fixture[1].write())

class BytesReadTestCase(unittest.TestCase):
    """
    Test case for L{fmspy.rtmp.packets.BytesRead}.
    """

    data = [
            (
                { 'header' : RTMPHeader(object_id=2, timestamp=0, length=4, type=0x03, stream_id=0L),
                  'buf'    : BufferedByteStream('\x00\x00\x00\x89'),
                },
                BytesRead(  bytes=137,
                            header=RTMPHeader(object_id=2, timestamp=0, length=4, type=0x03, stream_id=0L)),
            ),
           ]

    def test_eq(self):
        self.failUnlessEqual(BytesRead(bytes=5, header=RTMPHeader(object_id=3)), BytesRead(bytes=5, header=RTMPHeader(object_id=3)))
        self.failIfEqual(BytesRead(bytes=5, header=RTMPHeader(object_id=4)), BytesRead(bytes=5, header=RTMPHeader(object_id=3)))
        self.failIfEqual(BytesRead(bytes=6, header=RTMPHeader(object_id=3)), BytesRead(bytes=5, header=RTMPHeader(object_id=3)))

    def test_read(self):
        for fixture in self.data:
            fixture[0]['buf'].seek(0)
            self.failUnlessEqual(fixture[1], BytesRead.read(**fixture[0]))

    def test_write(self):
        for fixture in self.data:
            fixture[0]['buf'].seek(0)
            self.failUnlessEqual(fixture[0]['buf'].read(), fixture[1].write())

class PingTestCase(unittest.TestCase):
    """
    Test case for L{fmspy.rtmp.packets.Ping}.
    """

    data = [
            (
                { 'header' : RTMPHeader(object_id=2, timestamp=0, length=6, type=0x04, stream_id=0L),
                  'buf'    : BufferedByteStream('\x00\x06\x00\x00\x00\x89'),
                },
                Ping( event=6, data=[137],
                            header=RTMPHeader(object_id=2, timestamp=0, length=6, type=0x04, stream_id=0L)),
            ),
            (
                { 'header' : RTMPHeader(object_id=2, timestamp=0, length=10, type=0x04, stream_id=0L),
                  'buf'    : BufferedByteStream('\x00\x06\x00\x00\x00\x89\x00\x00\x00\x0e'),
                },
                Ping( event=6, data=[137, 14],
                            header=RTMPHeader(object_id=2, timestamp=0, length=10, type=0x04, stream_id=0L)),
            ),
            (
                { 'header' : RTMPHeader(object_id=2, timestamp=0, length=14, type=0x04, stream_id=0L),
                  'buf'    : BufferedByteStream('\x00\x06\x00\x00\x00\x89\x00\x00\x00\x0e\x00\x00\x03y'),
                },
                Ping( event=6, data=[137, 14, 889],
                            header=RTMPHeader(object_id=2, timestamp=0, length=14, type=0x04, stream_id=0L)),
            ),
           ]

    def test_eq(self):
        self.failUnlessEqual(Ping(event=5, data=[3], header=RTMPHeader(object_id=3)), Ping(event=5, data=[3], header=RTMPHeader(object_id=3)))
        self.failIfEqual(Ping(event=5, data=[3], header=RTMPHeader(object_id=3)), Ping(event=5, data=[3], header=RTMPHeader(object_id=4)))
        self.failIfEqual(Ping(event=5, data=[3], header=RTMPHeader(object_id=3)), Ping(event=5, data=[3, 4], header=RTMPHeader(object_id=3)))
        self.failIfEqual(Ping(event=5, data=[3], header=RTMPHeader(object_id=3)), Ping(event=6, data=[3], header=RTMPHeader(object_id=3)))

    def test_read(self):
        for fixture in self.data:
            fixture[0]['buf'].seek(0)
            self.failUnlessEqual(fixture[1], Ping.read(**fixture[0]))

    def test_write(self):
        for fixture in self.data:
            fixture[0]['buf'].seek(0)
            self.failUnlessEqual(fixture[0]['buf'].read(), fixture[1].write())
