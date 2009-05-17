# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Different RTMP packets.
"""

import pyamf
from pyamf.util import BufferedByteStream

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

    def __ne__(self, other):
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

    def __ne__(self, other):
        return not self.__eq__(other)

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

        @param name: procedure name
        @type name: C{str}
        @param argv: call arguments
        @type argv: C{list}
        @param id: request ID
        @type id: C{float}
        @param header: packet header
        @type header: L{RTMPHeader}
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

    def __ne__(self, other):
        return not self.__eq__(other)

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

class BytesRead(Packet):
    """
    Bytes read packet. 

    This packet is used (?) to control stream liveness.

    @ivar bytes: number of bytes received so far
    @type bytes: C{int}
    """

    def __init__(self, bytes, header=None):
        """
        Construct BytesRead packet.

        @param bytes: number of bytes received so far
        @type bytes: C{int}
        @param header: packet header
        @type header: L{RTMPHeader}
        """
        if header is None:
            header = RTMPHeader(constants.DEFAULT_BYTES_READ_OBJECT_ID, 0, 0, constants.BYTES_READ, 0)
        else:
            if header.type is None:
                header.type = constants.BYTES_READ
            if header.object_id is None:
                header.object_id = constants.DEFAULT_BYTES_READ_OBJECT_ID

        super(BytesRead, self).__init__(header)

        self.bytes = bytes

    def __repr__(self):
        return "<%s(bytes=%r, header=%r)>" % (self.__class__.__name__, self.bytes, self.header)

    def __eq__(self, other):
        if not isinstance(other, BytesRead):
            return NotImplemented

        return self.bytes == other.bytes and self.header == other.header

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def read(self, header, buf):
        """
        Read (decode) packet from stream.

        @param header: packet header
        @type header: L{RTMPHeader}
        @param buf: buffer holding packet data
        @type buf: C{BufferedByteStream}
        """
        return BytesRead(buf.read_ulong(), header)

    def write(self):
        """
        Encode packet into bytes.

        @return: representation of packet
        @rtype: C{str}
        """
        buf = BufferedByteStream()
        buf.write_ulong(self.bytes)
        self.header.length = len(buf)
        buf.seek(0, 0)
        return buf.read()

class Ping(Packet):
    """
    Ping packet is used (?) to check as connection keep-alive.

    @ivar event: ping event (1 byte)
    @type event: C{int}
    @ivar data: ping data, 1..3 longs (4 bytes * 1..3)
    @type data: C{list(int)}
    """
    
    STREAM_CLEAR = 0
    """ Stream clear event """
    STREAM_PLAYBUFFER_CLEAR = 1
    """ Stream play """
    UNKNOWN_2 = 2
    """ Unknown event """
    CLIENT_BUFFER = 3
    """ Client buffer """
    STREAM_RESET = 4
    """ Stream reset """
    UNKNOWN_5 = 5
    """ One more unknown event """
    PING_CLIENT = 6 
    """ Client ping event """
    PONG_SERVER = 7
    """ Server response event """
    UNKNOWN_8 = 8
    """ One more unknown event """
    UNDEFINED = -1
    """ Event type is undefined """

    def __init__(self, event, data, header=None):
        """
        Construct Ping packet.

        @param event: ping event (1 byte)
        @type event: C{int}
        @param data: ping data, 1..3 longs (4 bytes * 1..3)
        @type data: C{list(int)}
        @param header: packet header
        @type header: L{RTMPHeader}
        """
        if header is None:
            header = RTMPHeader(constants.DEFAULT_PING_OBJECT_ID, 0, 0, constants.PING, 0)
        else:
            if header.type is None:
                header.type = constants.PING
            if header.object_id is None:
                header.object_id = constants.DEFAULT_PING_OBJECT_ID

        super(Ping, self).__init__(header)

        self.event = event
        self.data = data

    def __repr__(self):
        return "<%s(event=%r, data=%r, header=%r)>" % (self.__class__.__name__, self.event, self.data, self.header)

    def __eq__(self, other):
        if not isinstance(other, Ping):
            return NotImplemented

        return self.event == other.event and self.data == other.data and self.header == other.header

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def read(self, header, buf):
        """
        Read (decode) packet from stream.

        @param header: packet header
        @type header: L{RTMPHeader}
        @param buf: buffer holding packet data
        @type buf: C{BufferedByteStream}
        """
        data = [-1]
        (event, data[0]) = (buf.read_ushort(), buf.read_ulong())
        if buf.remaining() >= 4:
            data.append(buf.read_ulong())
            if buf.remaining() >= 4:
                data.append(buf.read_ulong())

        return Ping(event, data, header)

    def write(self):
        """
        Encode packet into bytes.

        @return: representation of packet
        @rtype: C{str}
        """
        buf = BufferedByteStream()
        buf.write_ushort(self.event)

        for val in self.data:
            buf.write_ulong(val)

        self.header.length = len(buf)
        buf.seek(0, 0)
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
                constants.BYTES_READ : BytesRead,
                constants.PING : Ping,
              }

    if header.type in typeMap:
        return typeMap[header.type].read(header, buf)

    return DataPacket.read(header, buf)
