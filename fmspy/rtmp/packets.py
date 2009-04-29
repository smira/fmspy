# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Different RTMP packets.
"""

import pyamf

from fmspy.rtmp.header import RTMPHeader
from fmspy.rtmp import constants

class Packet(object):
    """
    Base RTMP packet.

    @ivar header: packet header
    @type header: L{RTMPHeader}
    """

    def __init__(self, header):
        """
        Create RTMP Packet.

        @param header: packet header
        @type header: L{RTMPHeader}
        """
        self.header = header

    def __repr__(self):
        return "<%s(header=%r)>" % (self.__class__.__name__, self.header)

    def __eq__(self, other):
        return NotImplemented

    @classmethod
    def read(self, header, buf):
        """
        Read (decode) packet from stream.

        @param header: packet header
        @type header: L{RTMPHeader}
        @param buf: buffer holding packet data
        @type buf: C{BufferedByteStream}
        """
        raise NotImplementedError

    def write(self):
        """
        Encode packet into bytes.

        @return: representation of packet
        @rtype: C{str}
        """
        raise NotImplementedError

class DataPacket(Packet):
    """
    Abstract RTMP packet, holding data.

    @ivar data: packet data (bytes)
    @type data: C{str}
    """

    def __init__(self, header, data):
        """
        Create RTMP Packet.

        @param header: packet header
        @type header: L{RTMPHeader}
        @param data: packet data (bytes)
        @type data: C{str}
        """
        super(DataPacket, self).__init__(header)
        self.data = data
        self.header.length = len(data)

    def __repr__(self):
        return "<%s(header=%r, data=%r)>" % (self.__class__.__name__, self.header, self.data)

    def __eq__(self, other):
        if not isinstance(other, DataPacket):
            return NotImplemented

        return self.data == other.data and self.header == other.header

    @classmethod
    def read(self, header, buf):
        """
        Read (decode) packet from stream.

        @param header: packet header
        @type header: L{RTMPHeader}
        @param buf: buffer holding packet data
        @type buf: C{BufferedByteStream}
        """
        return DataPacket(header=header, data=buf.read())

    def write(self):
        """
        Encode packet into bytes.

        @return: representation of packet
        @rtype: C{str}
        """
        return self.data

class Invoke(Packet):
    """
    Invoke RTMP Packet (RPC).

    Invoke packet invokes procedure named L{name} with arguments
    L{argv}. Calls-replies are matched using L{id}.

    @ivar name: procedure name
    @type name: C{str}
    @ivar id: request ID
    @type id: C{float}
    @ivar argv: call arguments
    @type argv: C{list}
    """

    def __init__(self, name, argv, id, header):
        """
        Construct Invoke packet.
        """
        if header.type is None:
            header.type = constants.INVOKE
        if header.object_id is None:
            header.object_id = constants.DEFAULT_INVOKE_OBJECT_ID

        super(Invoke, self).__init__(header)

        self.name = name
        self.argv = argv
        self.id = id

    def __repr__(self):
        return "<%s(name=%r, argv=%r, id=%r, header=%r)>" % (self.__class__.__name__, self.name, self.argv, self.id, self.header)

    def __eq__(self, other):
        if not isinstance(other, Invoke):
            return NotImplemented

        return self.name == other.name and self.argv == other.argv and self.id == other.id and self.header == other.header

    @classmethod
    def read(self, header, buf):
        """
        Read (decode) packet from stream.

        @param header: packet header
        @type header: L{RTMPHeader}
        @param buf: buffer holding packet data
        @type buf: C{BufferedByteStream}
        """
        amf = pyamf.decode(buf)
        name = amf.next()
        id = amf.next()
        argv = tuple(amf)
        return Invoke(name, argv, id, header)

    def write(self):
        """
        Encode packet into bytes.

        @return: representation of packet
        @rtype: C{str}
        """
        buf = pyamf.encode(self.name, self.id, *self.argv)
        self.header.length = len(buf)
        return buf.read()

def packetFactory(header, buf):
    """
    Find approriate class for packet decoding.

    @param header: packet header
    @type header: L{RTMPHeader}
    @param buf: buffer holding packet data
    @type buf: C{BufferedByteStream}
    @return: decoded packet
    @rtype: L{Packet}
    """
    typeMap = {
                constants.INVOKE : Invoke,
              }

    if header.type in typeMap:
        return typeMap[header.type].read(header, buf)

    return DataPacket.read(header, buf)
