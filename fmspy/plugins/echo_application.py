# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Example echo application.
"""

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log

from fmspy.application import Application

class EchoApplication(Application):
    """
    Example application: echo.

    Echo application sends back what it receives.
    """
    implements(IPlugin)

    def invoke_echo(self, protocol, value):
        """
        Handler for C{echo(value)}.

        Return the same value that was passed in.
        """
        return value

    def appConnect(self, protocol, path):
        """
        Client is connecting to application.

        Hook for custom application, may be deferred.

        If application wants to refuse client from connecting,
        it should raise some error.
        
        @param protocol: client protocol
        @type protocol: L{RTMPServerProtocol}
        @param path: extra connect path
        @type path: C{list}
        """
        log.msg("appConnect(%r, %r)" % (protocol, path))

    def appCreateRoom(self, protocol, room_name, path):
        """
        Room is about to be created for new client.

        Hook for custom application, may be deferred.

        If application wants to refuse client from creating this room,
        it should raise some error. This method isn't called
        for root room (L{hall}), root room is created implicitly
        for every application.
        
        @param protocol: client protocol
        @type protocol: L{RTMPServerProtocol}
        @param room_name: room name
        @type room_name: C{str}
        @param path: extra connect path
        @type path: C{list}
        """
        log.msg("appCreateRoom(%r, %r, %r)" % (protocol, room_name, path))
    
    def appEnterRoom(self, protocol, room, path):
        """
        Client is about to enter room.

        Hook for custom application, may be deferred.

        If application wants to refuse client from entering this room,
        it should raise some error.
        
        @param protocol: client protocol
        @type protocol: L{RTMPServerProtocol}
        @param room: room 
        @type room: L{Room}
        @param path: extra connect path
        @type path: C{list}
        """
        log.msg("appEnterRoom(%r, %r, %r)" % (protocol, room, path))

    def appLeaveRoom(self, protocol, room):
        """
        Client is leaving room.

        Hook for custom application, should return
        immediately. No exceptions should be raised
        in this method.

        @param protocol: client protocol
        @type protocol: L{RTMPServerProtocol}
        @param room: room 
        @type room: L{Room}
        """
        log.msg("appLeaveRoom(%r, %r)" % (protocol, room))
    
    def appDestroyRoom(self, room):
        """
        Room is about to be destroyed (it became empty).

        Hook for custom application, should return
        immediately. No exceptions should be raised
        in this method.

        @param room: room 
        @type room: L{Room}
        """
        log.msg("appDestroyRoom(%r)" % (room))

app = EchoApplication()
