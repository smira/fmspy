# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Base RTMP protocol.
"""

import copy

from twisted.internet import protocol, reactor, task, defer
from twisted.python import log
from pyamf.util import BufferedByteStream

from fmspy.rtmp.assembly import RTMPAssembler, RTMPDisassembler
from fmspy.rtmp import constants
from fmspy.rtmp.packets import Ping, BytesRead, Invoke
from fmspy.rtmp.header import RTMPHeader
from fmspy.rtmp.status import Status
from fmspy.config import config
from fmspy import _time

class UnhandledInvokeError(Exception):
    """
    Unable to handle invoke (no such method).
    """
    code = constants.StatusCodes.NC_CALL_FAILED

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
        Handshake complete, clear timeouts.
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
        log.msg("<- %r" % packet)
        handler = 'handle' + packet.__class__.__name__
        try:
            getattr(self, handler)(packet)
        except AttributeError:
            log.msg("Unhandled packet: %r" % packet)

    def pushPacket(self, packet):
        """
        Push outgoing RTMP packet.

        @param packet: outgoing packet
        @type packet: L{Packet}.
        """
        log.msg("-> %r" % packet)
        self.output.push_packet(packet)

class RTMPCoreProtocol(RTMPBaseProtocol):
    """
    RTMP Protocol: core features for all protocols.

    @ivar lastReceived: last time some data was received
    @type lastReceived: C{int}
    @ivar bytesReceived: number of bytes received so far
    @type bytesReceived: C{int}
    @ivar pingTask: periodic ping task
    @type pingTask: C{task.LoopingCall}
    @ivar nextInvokeId: next Invoke id to use in this connection
    @type nextInvokeId: C{float}
    @ivar invokeReplies: collection of C{Deferred}s for each L{Invoke} id we sent
    @type invokeReplies: C{dict}
    """

    def __init__(self):
        """
        Constructor.
        """
        RTMPBaseProtocol.__init__(self)
        self.bytesReceived = 0
        self.lastReceived = _time.seconds()
        self.pingTask = None
        self.nextInvokeId = 2.0
        self.invokeReplies = {}

    def dataReceived(self, data):
        """
        Some data was received from peer.

        @param data: bytes received
        @type data: C{str}
        """
        self.lastReceived = _time.seconds()
        self.bytesReceived += len(data)

        RTMPBaseProtocol.dataReceived(self, data)

    def connectionLost(self, reason):
        """
        Connection with peer was lost for some reason.
        """
        RTMPBaseProtocol.connectionLost(self, reason)

        self.invokeReplies = {}

        if self.pingTask is not None:
            self.pingTask.stop()
            self.pingTask = None

    def _handshakeComplete(self):
        """
        Handshake was complete.

        Start regular pings.
        """
        RTMPBaseProtocol._handshakeComplete(self)

        self.pingTask = task.LoopingCall(self._pinger)
        self.pingTask.start(config.getint('RTMP', 'pingInterval'), now=False)

    def handlePing(self, packet):
        """
        Handle incoming L{Ping} packets.

        @param packet: packet
        @type packet: L{Ping}
        """
        # stream buffer length, sending it to router, and sending buffer clear ping message
        if packet.event == Ping.CLIENT_BUFFER:
            self.pushPacket(Ping(Ping.STREAM_CLEAR, [packet.data[0]]))
        # normal ping request
        elif packet.event == Ping.PING_CLIENT:
            self.pushPacket(Ping(Ping.PONG_SERVER, packet.data))
        # normal pong
        elif packet.event == Ping.PONG_SERVER:
            pass # we control last received time in L{dataReceived}
        # first ping ?
        elif packet.event == Ping.UNKNOWN_8:
            pass
        else:
            log.msg("Unknown ping: %r" % packet)

    def handleBytesRead(self, packet):
        """
        Handle incoming L{BytesRead} packets.

        @param packet: packet
        @type packet: L{BytesRead}
        """
        pass # we do nothing

    def _pinger(self):
        """
        Regular 'ping' service.

        We send 'pings' to other end of RTMP protocol, expecting to receive
        'pong'. If we receive some data, we assume 'ping' is sent. If other end
        of protocol doesn't send anything in reply to our 'ping' for some timeout,
        we disconnect connection.
        """
        noDataInterval = _time.seconds() - self.lastReceived

        if noDataInterval > config.getint('RTMP', 'keepAliveTimeout'):
            log.msg('Closing connection due too much inactivity (%d)' % noDataInterval)
            self.transport.loseConnection()
            return

        if noDataInterval > config.getint('RTMP', 'pingInterval'):
            self.pushPacket(Ping(Ping.PING_CLIENT, [int(_time.seconds()*1000) & 0x7fffffff]))

        self.pushPacket(BytesRead(self.bytesReceived))

    def _first_ping(self):
        """
        Send first ping, usually after first connect.
        """
        self.pushPacket(Ping(Ping.UNKNOWN_8, [0, 1, int(_time.seconds()*1000) & 0x7fffffff]))

    def handleInvoke(self, packet):
        """
        Handle incoming L{Invoke} packets.

        @param packet: packet
        @type packet: L{Invoke}
        """
        if packet.name in ["_result", "_error"]:
            # we got result for some our invoke
            if packet.id not in self.invokeReplies:
                log.msg("Got reply %r for unsent (?) Invoke" % packet)
            else:
                d = self.invokeReplies.pop(packet.id)

                if packet.name == "_result":
                    d.callback(packet.argv)
                else:
                    d.errback(Status(**packet.argv[1]))

            return 

        handler = getattr(self, 'invoke_' + packet.name.lower(), None)
        if handler is None:
            handler = self.defaultInvokeHandler

        def gotResult(result):
            """
            Got result from invoke.
            """
            self.pushPacket(Invoke(header=copy.copy(packet.header), id=packet.id, name="_result", argv=result))

        def gotError(failure):
            """
            Invoke resulted in some error.
            """
            log.err(failure, "Error while handling invoke")
            self.pushPacket(Invoke(header=copy.copy(packet.header), id=packet.id, name="_error", argv=[None, Status.from_failure(failure)]))

        defer.maybeDeferred(handler, packet, *packet.argv).addCallbacks(gotResult, gotError)

    def invoke(self, name, *args):
        """
        Perform invoke on other side of connection.

        @param name: method being invoked
        @type name: C{str}
        @param args: arguments for the call
        @type args: C{list}
        """
        packet = Invoke(name, (None, ) + args, self.nextInvokeId, RTMPHeader(timestamp=0, stream_id=0))
        d = self.invokeReplies[self.nextInvokeId] = defer.Deferred()
        self.nextInvokeId += 1
        self.pushPacket(packet)

        return d

    def defaultInvokeHandler(self, packet,  *args):
        """
        Should be overridden.

        Process packet when no default handler established.
        """
        log.msg("Unhandled invoke: %s(%r) [%d]" % (packet.name, args, packet.header.object_id))
        raise UnhandledInvokeError(packet.name)



