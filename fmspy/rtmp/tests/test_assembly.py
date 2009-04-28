# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.rtmp.assembly}.
"""

import unittest
import struct
import random

from pyamf.util import BufferedByteStream

from fmspy.rtmp.header import RTMPHeader
from fmspy.rtmp.packets import DataPacket
from fmspy.rtmp.assembly import RTMPDisassembler, RTMPAssembler

class RTMPMockDisassembler(RTMPDisassembler):
    """
    Mock decoding all packets into L{DataPacket}.
    """

    def _decode_packet(self, header, buf):
        return DataPacket.read(header, buf)

    def is_empty(self):
        return len(self.buffer) == 0

class RTMPAssemblyTestCase(unittest.TestCase):
    """
    Base test case for L{fmspy.rtmp.assembly}.
    """

    data = [ 
                {
                    'data' : [  0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ],
                    'packets' : [DataPacket(header=RTMPHeader(object_id=2, timestamp=0, length=6, type=0x04, stream_id=0), data="\x00\x00\x00\x00\x00\x01")]
                },
                {
                    'data' : [  0x02, 0x91, 0x06, 0xe6, 0x00, 0x00, 0x0a, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 
                                0x01, 0x6b, 0x00, 0x00, 0x42, 0x14, 0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x04, 0x70, 0x6c, 0x61, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                                0x00, 0x00, 0x05, 0x02, 0x00, 0x2e, 0x31, 0x39, 0x35, 0x31, 0x32, 0x39, 0x5f, 0x31, 0x34, 0x34, 0x30, 0x35, 0x30, 0x5f, 0x62, 0x30, 0x36, 0x36, 
                                0x36, 0x32, 0x65, 0x37, 0x39, 0x39, 0x61, 0x35, 0x36, 0x37, 0x61, 0x30, 0x66, 0x37, 0x64, 0x61, 0x33, 0x65, 0x39, 0x63, 0x30, 0x30, 0x65, 0x33, 
                                0x35, 0x34, 0x35, 0x36 ],
                    'packets' : [DataPacket(header=RTMPHeader(object_id=2, timestamp=9504486, length=10, type=0x04, stream_id=0),
                                    data='\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00'), 
                                 DataPacket(header=RTMPHeader(object_id=8, timestamp=363, length=66, type=0x14, stream_id=16777216),
                                    data='\x02\x00\x04play\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x02\x00.195129_144050_b06662e799a567a0f7da3e9c00e35456')
                                ],
                },
                {
                    'data' : [  0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x63, 0x6f, 0x75, 0x6e, 0x74, 0x4f, 0x6e, 0x6c, 0x69, 0x6e, 
                                0x65, 0x72, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x43, 0x00, 0x00, 0x00, 
                                0x00, 0x00, 0x24, 0x13, 0x00, 0x11, 0x62, 0x72, 0x6f, 0x61, 0x64, 0x63, 0x61, 0x73, 0x74, 0x53, 0x79, 0x6e, 0x63, 0x44, 
                                0x61, 0x74, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 
                                0xc3, 0x00, 0x11, 0x62, 0x72, 0x6f, 0x61, 0x64, 0x63, 0x61, 0x73, 0x74, 0x53, 0x79, 0x6e, 0x63, 0x44, 
                                0x61, 0x74, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
                                0x43, 0x00, 0x01, 0x6b, 
                                0x00, 0x00, 0x19, 0x14, 0x02, 0x00, 0x0c, 0x63, 0x72, 0x65, 0x61, 0x74, 0x65, 0x53, 0x74, 0x72, 0x65, 0x61, 0x6d, 0x00, 
                                0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05],
                    'packets' : [DataPacket(header=RTMPHeader(object_id=3, timestamp=0, length=32, type=0x13, stream_id=0L), 
                                    data='\x00\rcountOnliners\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'), 
                                 DataPacket(header=RTMPHeader(object_id=3, timestamp=0, length=36, type=0x13, stream_id=0L), 
                                    data='\x00\x11broadcastSyncData\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'), 
                                 DataPacket(header=RTMPHeader(object_id=3, timestamp=0, length=36, type=0x13, stream_id=0L), 
                                    data='\x00\x11broadcastSyncData\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'), 
                                 DataPacket(header=RTMPHeader(object_id=3, timestamp=363, length=25, type=0x14, stream_id=0L),
                                    data='\x02\x00\x0ccreateStream\x00@\x00\x00\x00\x00\x00\x00\x00\x05')],
                }
    ] 

    def gen_packet(self, header, shortHeaders, data, l, chunkSize):
        h = list(header)
        h[4:7] = struct.pack("!L", l)[1:4]
        h = ''.join(h)
        yield h
        first = min(chunkSize, l)
        yield data[0:first]
        for pos in xrange(first, l, chunkSize):
            yield random.choice(shortHeaders)
            yield data[pos:pos+chunkSize]

class RTMPDisassemblerTestCase(RTMPAssemblyTestCase):
    """
    Test case for L{fmspy.rtmp.assembly.RTMPDisassembler}.
    """

    def test_disassemble(self):
        for fixture in self.data:
            d = RTMPMockDisassembler(128)
            self.assertEqual(fixture['packets'], d.push_data(struct.pack("B" * len(fixture['data']), *fixture['data'])).disassemble_packets())
            self.failUnless(d.is_empty())

    def test_disassemble_chunks(self):
        chunkSizes = (32, 64, 128, 256)
        header = "\x02\x00\x00\x00\x00\x00\x06\x04\x00\x00\x00\x00"
        shortHeaders = ["\xc2", "\x82\x00\x00\x00"]

        for chunkSize in chunkSizes:
            d = RTMPMockDisassembler(chunkSize)
            for l in xrange(1, 258):
                data = ''.join([chr(random.randint(0, 255)) for x in xrange(l)])

                self.failUnlessEqual([DataPacket(header=RTMPHeader(object_id=2, timestamp=0, length=0, type=0x04, stream_id=0), data=data)], 
                        d.push_data(''.join(self.gen_packet(header, shortHeaders, data, l, chunkSize))).disassemble_packets())
                self.failUnless(d.is_empty())


class RTMPAssemblerTestCase(RTMPAssemblyTestCase):
    """
    Test case for L{fmspy.rtmp.assembly.RTMPAssembler}.
    """

    def test_assemble(self):
        for fixture in self.data:
            buf = BufferedByteStream()
            a = RTMPAssembler(128, buf)

            for packet in fixture['packets']:
                a.push_packet(packet)

            buf.seek(0, 0)

            self.failUnlessEqual(struct.pack("B" * len(fixture['data']), *fixture['data']), buf.read())

    def test_assemble_chunks(self):
        chunkSizes = (32, 64, 128, 256)
        header = RTMPHeader(object_id=2, timestamp=9504486, length=10, type=0x04, stream_id=0)

        for chunkSize in chunkSizes:
            for l in xrange(1, 258):
                data = ''.join([chr(random.randint(0, 255)) for x in xrange(l)])

                buf = BufferedByteStream()
                a = RTMPAssembler(chunkSize, buf)
                a.push_packet(DataPacket(header=header, data=data))

                buf.seek(0, 0)
                self.failUnlessEqual(''.join(self.gen_packet("\x02\x91\x06\xe6\x00\x00\x01\x04\x00\x00\x00\x00", ["\xc2"], data, l, chunkSize)), buf.read())
