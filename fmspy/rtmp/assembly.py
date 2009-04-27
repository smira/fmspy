# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
RTMP packet disassembly/assembly line.

Cutting packets into chunks for transmission.
"""

from pyamf.util import BufferedByteStream

from fmspy.rtmp.header import RTMPHeader, NeedBytes

class RTMPDisassembler(object):
    """
    Disassembling bytestream into RTMP packets.

    RTMP stream slices packets into chunks of L{chunkSize}. This class
    processes incoming stream of RTMP protocol data (after initial handshake)
    and decodes RTMP packets.

    Communication goes independently for each object_id. Last received
    headers are stored for each object_id in L{lastHeaders}. L{pool} holds
    incomplete packet contents also for each object_id.

    @ivar lastHeaders: last received header for object_id
    @type lastHeaders: C{dict}, object_id -> L{RTMPHeader}
    @ivar pool: incomplete packet data for object_id
    @type pool: C{dict}, object_id -> L{BufferedByteStream}
    @ivar chunkSize: size of chunk for this stream
    @type chunkSize: C{int}
    @ivar buffer: incoming buffer with data received from protocol
    @type buffer: L{BufferedByteStream}
    """

    def __init__(self, chunkSize):
        """
        Constructor.

        @param chunkSize: initial size of chunk
        @type chunkSize: C{int}
        """
        self.lastHeaders = {}
        self.pool = {}
        self.chunkSize = chunkSize
        self.buffer = BufferedByteStream()

    def push_data(self, data):
        """
        Push more incoming data, decode packets received so far.

        @param data: data received
        @type data: C{str}
        @return: decoded packets, list of L{Packet}
        @rtype: C{list}
        """

        self.buffer.seek(0, 2)
        self.buffer.write(data)

        return self._disassemble()

    def _disassemble(self):
        """
        Disassemble L{buffer} into packets.

        @return: decoded packets, list of L{Packet}
        @rtype: C{list}
        """
        result = []

        self.buffer.seek(0)

        # while we have some data to analyze
        while self.buffer.remaining() > 0:
            try:
                # try to parse header from stream
                header = RTMPHeader.read(self.buffer)
            except NeedBytes, (bytes, ):
                # not enough bytes, return what we've already parsed
                return result

            # fill header with extra data from previous headers received
            # with same object_id
            header.fill(self.lastHeaders.get(header.object_id, RTMPHeader()))

            # get buffer for data of this packet
            buf = self.pool.get(header.object_id, BufferedByteStream())

            # this chunk size is minimum of regular chunk size in this
            # disassembler and what we have left here
            thisChunk = min(header.length - len(buf), self.chunkSize)
            if self.buffer.remaining() < thisChunk:
                # we have not enough bytes to read this chunk of data
                return result
   
            # we got complete chunk
            buf.write(self.buffer.read(thisChunk))

            # store packet header for this object_id
            self.lastHeaders[header.object_id] = header

            # skip data left in input buffer
            self.buffer.consume()

            # this chunk completes full packet?
            if len(buf) < header.length:
                # no, store buffer for further chunks
                self.pool[header.object_id] = buf
            else:
                # parse packet from header and data
                buf.seek(0, 0)
                result.append(self._decode_packet(header, buf))

                # delete stored data for this packet
                if header.object_id in self.pool:
                    del self.pool[header.object_id]

        return result

    def _decode_packet(self, header, buf):
        """
        Decode received packet.

        @param header: header of packet
        @type header: L{RTMPHeader}
        @param buf: buffer holding packet data
        @type buf: L{BufferedByteStream}
        @return: decoded packet
        @rtype: L{Packet}
        """
        raise NotImplementedError
