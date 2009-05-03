# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Client RTMP protocol.
"""

from fmspy.rtmp.protocol.base import RTMPCoreProtocol
from fmspy.rtmp import constants

class RTMPClientProtocol(RTMPCoreProtocol):
    """
    RTMP client-side protocol implementation.
    """

    def _beginHandshake(self):
        """
        Begin handshake procedures.

        Clients sends initial handshake.
        """
        self.transport.write("\x03")
        self.transport.write("\x00" * constants.HANDSHAKE_SIZE)

    def _handshakeSendReceived(self):
        """
        Data received in HANDSHAKE_SEND state.

        Server sends handshake data two times, we return handshake back.
        """
        if len(self.handshakeBuf) < 2*constants.HANDSHAKE_SIZE + 1:
            return

        self.handshakeBuf.seek(0)
        assert self.handshakeBuf.read_uchar() == 0x03
        self.handshakeBuf.seek(constants.HANDSHAKE_SIZE + 1, 0)
        serverHandshake = self.handshakeBuf.read(constants.HANDSHAKE_SIZE)

        self.transport.write("\x03")
        self.transport.write(serverHandshake)

        self.handshakeBuf.consume()
        self._handshakeComplete()

    def _handshakeVerifyReceived(self):
        """
        Data received in HANDSHAKE_VERIFY state.

        Shouldn't get here in client mode.
        """
        assert False

