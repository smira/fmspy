# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Server RTMP protocol.
"""

from twisted.internet import protocol, defer
from twisted.python import log

from fmspy.rtmp.protocol.base import RTMPCoreProtocol, UnhandledInvokeError
from fmspy.rtmp import constants
from fmspy.rtmp.status import Status
from fmspy.application import app_factory

class AppStorage(object):
    """
    Class represents are for application to store
    data, associated with client.

    Each L{RTMPServerProtocol} holds instance of L{AppStorage} in
    property C{_app}.

    @ivar room: application room
    @type room: L{Room}
    """

class RTMPServerProtocol(RTMPCoreProtocol):
    """
    RTMP server-side protocol implementation.

    @ivar application: application bound to this protocol
    @type application: L{Application}
    """

    def __init__(self):
        """
        Constructor.
        """
        RTMPCoreProtocol.__init__(self)
        
        self.application = None
        self._app = AppStorage()

    def connectionLost(self, reason):
        """
        Connection with peer was lost for some reason.
        """
        if self.application is not None:
            self.application.disconnect(self)
            self.application = None
            self._app = None

        RTMPCoreProtocol.connectionLost(self, reason)

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

    def invoke_connect(self, packet, connect_params):
        """
        Connection to server application.

        @param packet: original Invoke packet
        @type packet: L{Invoke}
        @param connect_params: connection params
        @type connect_params: C{dict}
        """
        log.msg("Connect to %r, Flash %s" % (connect_params['app'], connect_params['flashVer']))

        self._first_ping()

        connect_path = connect_params['app'].split('/')
        app_name = connect_path[0]
        del connect_path[0]

        self.application = app_factory.get_application(app_name)

        def connectOk(_):
            """
            Connection was successful, send message to client.
            """
            return [None, Status(constants.StatusCodes.NC_CONNECT_SUCCESS, "success", "Connect OK")]

        return self.application.connect(self, connect_path).addCallback(connectOk)

    def defaultInvokeHandler(self, packet,  *args):
        """
        Dispatch invokes to current application.
        """
        assert self.application is not None

        handler = getattr(self.application, 'invoke_' + packet.name.lower(), None)
        
        if handler is None:
            raise UnhandledInvokeError(packet.name)

        def gotResult(result):
            return [None, result]

        return defer.maybeDeferred(handler, self, *args[1:]).addCallback(gotResult)

class RTMPServerFactory(protocol.ServerFactory):
    """
    Construct RTMP server protocol.
    """
    protocol = RTMPServerProtocol
