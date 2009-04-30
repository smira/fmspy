# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Base RTMP protocol.
"""

from twisted.internet import protocol, reactor
from twisted.python import log
from pyamf.util import BufferedByteStream

from fmspy.rtmp.assembly import RTMPAssembler, RTMPDisassembler
from fmspy.rtmp import constants
from fmspy.config import config

class RTMPBaseProtocol(protocol.Protocol):
    """
    Basis RTMP protocol implementation.

    @ivar state: internal state of protocol
    @ivar input: input packet disassebmbler 
    @type input: L{RTMPDisassembler}
    @ivar output: output packet assembler
    @type output: L{RTMPAssembler}
    @ivar handshakeBuf: buffer, holding input data during handshake
    @type handshakeBuf: C{BufferedByteStream}
    """

    class State:
        CONNECTING = 'connecting'
        """
        Connection in progress
        """
        HANDSHAKE_SEND = 'handshake-send'
        """
        Handshake, 1st phase.
        """
        HANDSHAKE_VERIFY = 'handshake-verify'
        """
        Handshake, 2nd phase.
        """
        RUNNING = 'running'
        """
        Usual state of protocol: receiving-sending RTMP packets.
        """

    def __init__(self):
        """
        Constructor.
        """
        self.state = self.State.CONNECTING
        self.handshakeTimeout = None

    def connectionMade(self):
        """
        Successfully connected to peer.
        """
        self.input = RTMPDisassembler(constants.DEFAULT_CHUNK_SIZE)
        self.output = RTMPAssembler(constants.DEFAULT_CHUNK_SIZE, self.transport)

        self.state = self.State.HANDSHAKE_SEND
        self.handshakeTimeout = reactor.callLater(config.getint('RTMP', 'handshakeTimeout'), self._handshakeTimedout)
        self.handshakeBuf = BufferedByteStream()
        self._beginHandshake()

    def _beginHandshake(self):
        """
        Begin handshake procedures.

        Implemented in descendants.
        """
        raise NotImplementedError

    def _handshakeSendReceived(self):
        """
        Data received in HANDSHAKE_SEND state.

        Implemented in descendants.
        """
        raise NotImplementedError

    def _handshakeVerifyReceived(self):
        """
        Data received in HANDSHAKE_VERIFY state.

        Implemented in descendants.
        """
        raise NotImplementedError

    def _handshakeComplete(self):
        """
        Handshake completed, clear timeouts.
        """
        if self.handshakeTimeout is not None:
            self.handshakeTimeout.cancel()
            self.handshakeTimeout = None
        self.state = self.State.RUNNING
        self._regularInput(self.handshakeBuf.read())
        del self.handshakeBuf

    def _handshakeTimedout(self):
        """
        Handshake not completed in timeout.
        """
        self.handshakeTimeout = None
        self.transport.loseConnection()

    def connectionLost(self, reason):
        """
        Connection with peer was lost for some reason.
        """
        if self.handshakeTimeout is not None:
            self.handshakeTimeout.cancel()
            self.handshakeTimeout = None

    def _regularInput(self, data):
        """
        Regular RTMP dataflow: stream of RTMP packets.

        Some bytes (L{data}) was received.

        @param data: bytes received
        @type data: C{str}
        """
        self.input.push_data(data)

        while True:
            packet = self.input.disassemble()
            if packet is None:
                return

            self._handlePacket(packet)

    def dataReceived(self, data):
        """
        Some data was received from peer.

        @param data: bytes received
        @type data: C{str}
        """
        if self.state == self.State.RUNNING:
            self._regularInput(data)
        else: # handshake
            self.handshakeBuf.seek(0, 2)
            self.handshakeBuf.write(data)
            if self.state == self.State.HANDSHAKE_SEND:
                self._handshakeSendReceived()
            elif self.state == self.State.HANDSHAKE_VERIFY:
                self._handshakeVerifyReceived()

    def _handlePacket(self, packet):
        """
        Dispatch received packet to some handler.

        @param packet: packet
        @type packet: L{Packet}
        """
        handler = 'handle_' + packet.__class__.__name__.lower()
        try:
            getattr(self, handler)(packet)
        except AttributeError:
            log.msg("Unhandled packet: %r" % packet)

