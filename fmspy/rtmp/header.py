# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
RTMP packet headers.
"""

from pyamf.util import BufferedByteStream

class NeedBytes(Exception):
    """
    Reading from packet requires some more bytes.
    """

class RTMPHeader(object):
    """
    RTMP Header holder class.

    RTMP Packets consist of a fixed-length header and a variable 
    length body that has a default of 128 bytes. The header can 
    come in one of four sizes: 12, 8, 4, or 1 byte(s).

    The two most significant bits of the first byte of the packet 
    (which also counts as the first byte of the header) determine the length 
    of the header. They can be extracted by ANDing the byte with the mask 0xC0. 
    The possible header lengths are specified below: 

     - B{00} - 12 bytes
     - B{01} - 8 bytes
     - B{10} - 4 bytes
     - B{11} - 1 byte

    The header excludes information in the shorter version and implies 
    that the information that is excluded is the same as the last time that 
    information was explicitly included in the header.

    In a full 12 byte header is broken down as follows:

     - The first byte has the header size and the object id. The first 
       two bits are the size of the header and the following 6 bits are the object 
       id. This limits a RTMP packets to a maximum of 64 objects in one packet. 
       This byte is always sent no matter the size of the header.
     - The next three bytes are the time stamp. This is a big-endian integer and 
       it is sent whenever the header size is 4 bytes or larger.
     - The next three bytes are the length of the object body. This is an integer 
       and is big-endian. The length of the object is the size of the AMF in the 
       RTMP packet without the RTMP headers, so you need to remove any RTMP headers 
       before this number matches properly. These bytes are sent whenever the header 
       size is 8 or more.
     - The next single byte is the content type. The content types are listed 
       in another section this page and are only included when the header is 8 bytes 
       or longer.
     - The final 4 bytes of the header is a stream id. This is a 32 bit integer 
       that is little-endian encoded. These bytes are only included when the header 
       is a full 12 bytes.

    @ivar object_id: Object ID
    @type object_id: C{int}
    @ivar timestamp: timestamp
    @type timestamp: C{int}
    @ivar length: length of packet body
    @type length: C{int}
    @ivar type: type of packet
    @type type: C{int}
    @ivar stream_id: Stream ID
    @type stream_id: C{int}
    """

    def __init__(self, object_id=None, timestamp=None, length=None, type=None, stream_id=None):
        """
        Construct header.

        @param object_id: Object ID
        @type object_id: C{int}
        @param timestamp: timestamp
        @type timestamp: C{int}
        @param length: length of packet body
        @type length: C{int}
        @param type: type of packet
        @type type: C{int}
        @param stream_id: Stream ID
        @type stream_id: C{int}
        """
        self.object_id = object_id
        self.timestamp = timestamp
        self.length = length
        self.type = type
        self.stream_id = stream_id

    def __repr__(self):
        return "<RTMPHeader(object_id=%r, timestamp=%r, length=%r, type=0x%02x, stream_id=%r)>" % (self.object_id,
                self.timestamp, self.length, self.type or 0, self.stream_id)

    def __eq__(self, other):
        if not isinstance(other, RTMPHeader):
            return NotImplemented

        return (self.object_id == other.object_id and self.timestamp == other.timestamp and
            self.length == other.length and self.type == other.type and
            self.stream_id == other.stream_id)

    def __ne__(self, other):
        return not self.__eq__(other)

    def fill(self, other):
        """
        Refill incomplete header with other header's data.

        This header (self) can be incomplete right-to-left, for example,
        if it was read from shortened format.

        @param other: source header (where we take values)
        @type other: L{RTMPHeader}
        """
        if self.stream_id is None:
            self.stream_id = other.stream_id

            if self.type is None:
                self.type = other.type

                if self.length is None:
                    self.length = other.length

                    if self.timestamp is None:
                        self.timestamp = other.timestamp

        assert self.stream_id is not None
        assert self.type is not None
        assert self.length is not None
        assert self.timestamp is not None
        assert self.object_id is not None

    def diff(self, other):
        """
        Find difference between this header and other header (how many fields differ).

        @param other: other header
        @type other: L{RTMPHeader}
        @return: difference
        @rtype: C{int}
        """
        if self is other or self == other:
            # headers are equal, we need 1 byte
            return 0

        # difference should be computed for packets with same object_id
        assert self.object_id == other.object_id

        if self.stream_id == other.stream_id:
            if self.type == other.type and self.length == other.length:
                # difference only in timestamp, 4 bytes
                return 1

            # stream_id matches, we need 8 bytes
            return 2
        
        # we need full header encoded, 12 bytes
        return 3

    @classmethod
    def read(cls, buf):
        """
        Read (parse, decode) header from bytestream.

        @param buf: buffer holding data for packet
        @type buf: C{BufferedByteStream}
        @raises NeedBytes: if we don't have enough bytes in buf
        """
        has_bytes = buf.remaining()
        if has_bytes < 1:
            raise NeedBytes, 1

        first = buf.read_uchar()

        size = (((first & 0xc0) >> 6) ^ 0x3) << 2
        if size == 0:
            size = 1

        if has_bytes < size:
            raise NeedBytes, size-has_bytes

        object_id = first & 0x3f
        timestamp = length = type = stream_id = None

        if size != 1:
            timestamp = buf.read_24bit_uint()

        if size >= 8:
            length = buf.read_24bit_uint()
            type = buf.read_uchar()

        if size == 12:
            stream_id = buf.read_ulong()

        return RTMPHeader(object_id, timestamp, length, type, stream_id)

    def write(self, previous=None):
        """
        Write (encoder) header to byte string.

        @param previous: previous header (used to compress header)
        @type previous: L{RTMPHeader}
        @return: encoded header
        @rtype: C{str}
        """
        if previous is None:
            diff = 3
        else:
            diff = self.diff(previous)

        first = self.object_id & 0x3f | ((diff ^ 3) << 6)

        if diff == 0:
            return chr(first)

        buf = BufferedByteStream()
        buf.write_uchar(first)

        buf.write_24bit_uint(self.timestamp)

        if diff > 1:
            buf.write_24bit_uint(self.length)
            buf.write_uchar(self.type)

            if diff > 2:
                buf.write_ulong(self.stream_id)

        buf.seek(0, 0)
        return buf.read()

