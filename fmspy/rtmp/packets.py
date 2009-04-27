# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Different RTMP packets.
"""

from fmspy.rtmp.header import RTMPHeader

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
        return "<%s header=%r>" % (self.__class__.__name__, self.header)

    def __eq__(self, other):
        return NotImplemented

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
        return "<%s header=%r data=%r>" % (self.__class__.__name__, self.header, self.data)

    def __eq__(self, other):
        if not isinstance(other, DataPacket):
            return NotImplemented

        return self.data == other.data and self.header == other.header

class Invoke(Packet):
    """
    Invoke RTMP Packet (RPC).

    @param name: procedure name
    @type name: C{str}
    @param id: request ID
    @type id: C{float}
    @param argv: call arguments
    @type argv: C{list}
    """





