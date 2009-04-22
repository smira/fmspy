# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
RTMP packet headers.
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

    def __init__(self, object_id, timestamp, length, type, stream_id):
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
        return "<RTMPHeader(object_id=%d, timestamp=%d, length=%d, type=0x%02x, stream_id=%d>" % (self.object_id,
                self.timestamp, self.length, self.type, self.stream_id)

    def __eq__(self, other):
        if not isinstance(other, RTMPHeader):
            raise NotImplemented

        return (self.object_id == other.object_id and self.timestamp == other.timestamp and
            self.length == other.length and self.type == other.type and
            self.stream_id == other.stream_id)

