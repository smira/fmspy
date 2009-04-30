# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Server RTMP protocol.
"""

from twisted.internet import protocol

from fmspy.rtmp.protocol.base import RTMPBaseProtocol
from fmspy.rtmp import constants

class RTMPServerProtocol(RTMPBaseProtocol):
    """
    RTMP server-side protocol implementation.
    """

    def _beginHandshake(self):
        """
        Begin handshake procedures.

        Server does nothing - it waits for handshake from client.
        """
        pass

    def _handshakeSendReceived(self):
        """
        Data received in HANDSHAKE_SEND state.

        Server waits for handshake from client, then sends it back to 
        client two times.
        """
        if len(self.handshakeBuf) < constants.HANDSHAKE_SIZE + 1:
            return

        self.handshakeBuf.seek(0)
        assert self.handshakeBuf.read_uchar() == 0x03
        clientHandshake = self.handshakeBuf.read(constants.HANDSHAKE_SIZE)

        self.transport.write("\x03")
        self.transport.write(clientHandshake * 2)

        self.handshakeBuf.consume()
        self.state = self.State.HANDSHAKE_VERIFY

    def _handshakeVerifyReceived(self):
        """
        Data received in HANDSHAKE_VERIFY state.

        Client should send back our handshake.
        """
        if len(self.handshakeBuf) < constants.HANDSHAKE_SIZE + 1:
            return

        self.handshakeBuf.seek(constants.HANDSHAKE_SIZE, 0)
        self.handshakeBuf.consume()

        self._handshakeComplete()

class RTMPServerFactory(protocol.ServerFactory):
    """
    Construct RTMP server protocol.
    """
    protocol = RTMPServerProtocol
