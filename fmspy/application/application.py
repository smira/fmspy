# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Base application class.
"""

import ConfigParser

from zope.interface import implements
from twisted.internet import defer

from fmspy.application.room import Room
from fmspy.application.interfaces import IApplication
from fmspy.config import config

class Application(object):
    """
    Base FMSPy application.

    @ivar hall: default room of application
    @type hall: L{Room}
    @ivar rooms: named application rooms
    @type rooms: C{dict}
    """
    implements(IApplication)

    def __init__(self):
        """
        Construct application.
        """
        self.hall = Room(self)
        self.rooms = {}

    def room_empty(self, room):
        """
        Hook, called when room becomes empty.

        @param room: empty room
        @type room: L{Room}
        """
        if room is self.hall:
            return

        self.appDestroyRoom(room)
        del self.rooms[room.name]
        room.dismiss()

    def name(self):
        """
        Get application name.

        Application name is used as entry point 
        during RTMP connect call.

        @rtype: C{str}
        """
        return config.get(self.__class__.__name__, 'name')

    def enabled(self):
        """
        Is application enabled or not?

        @rtype: C{bool}
        """
        try:
            return config.getboolean(self.__class__.__name__, 'enabled')
        except ConfigParser.Error:
            return False

    def load(self):
        """
        Potentially Deferred action that is called
        on application being loaded.

        Deferred can delay server startup (for example, connecting
        to database).
        """
        pass # nothing to do

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def connect(self, protocol, path):
        """
        Connect to application.

        Some client requested connection to this app.
        This method is called by L{RTMPServerProtocol}
        when new connection to app is established.

        @param protocol: client protocol
        @type protocol: L{RTMPServerProtocol}
        @param path: extra connect path
        @type path: C{list}
        @return: Deferred, connection status
        @rtype: C{Deferred}
        """
        def checkRoom(_):
            """
            Find out room from connection path.

            @return: Deferred or instant room for this connection
            @rtype: L{Room}
            """
            if not path:
                # Connect to root room, hall
                return (self.hall, [])

            # Room name is first param in path
            room_name, pathextra = path[0], path[1:]

            # Room is not created at the moment
            if room_name not in self.rooms:
                def createRoom(_):
                    """
                    Application allowed to create room.
                    """
                    self.rooms[room_name] = Room(self, room_name)
                    return (self.rooms[room_name], pathextra)

                return defer.maybeDeferred(self.appCreateRoom, protocol, room_name, pathextra).addCallback(createRoom)

            return (self.rooms[room_name], pathextra)

        def enterRoom(params):
            """
            We should figure out whether it is 
            allowed to join this room, and 
            perform actual join.
            """
            (room, pathextra) = params

            def realEnterRoom(_):
                room.enter(protocol)
                protocol._app.room = room

            def cleanupRoom(f):
                if room.empty() and room is not self.hall:
                    self.appDestroyRoom(room)
                    del self.rooms[room.name]

                return f

            return defer.maybeDeferred(self.appEnterRoom, protocol, room, pathextra).addCallbacks(realEnterRoom, cleanupRoom)

        return defer.maybeDeferred(self.appConnect, protocol, path).addCallback(checkRoom).addCallback(enterRoom)

    def disconnect(self, protocol):
        """
        Disconnect from application.

        @param protocol: client protocol
        @type protocol: L{RTMPServerProtocol}
        """
        self.appLeaveRoom(protocol, protocol._app.room)
        protocol._app.room.leave(protocol)
        del protocol._app.room

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
    
    def appDestroyRoom(self, room):
        """
        Room is about to be destroyed (it became empty).

        Hook for custom application, should return
        immediately. No exceptions should be raised
        in this method.

        @param room: room 
        @type room: L{Room}
        """

