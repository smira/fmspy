# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Application rooms.
"""

class Room(object):
    """
    Room (scope, context) is location inside application where clients meet.

    Room holds server objects: streams, shared objects, etc. It can be
    used to iterate over clients in room.

    @ivar clients: set of clients inside room
    @type clients: C{set}
    @ivar name: room name
    @type name: C{str}
    @ivar application: application owning this room
    @type application: L{Application}
    """

    def __init__(self, application, name='_'):
        """
        Construct new room.

        @param application: application owning this room
        @type application: L{Application}
        @param name: room name
        @type name: C{str}
        """
        self.name = name
        self.application = application
        self.clients = set()

    def dismiss(self):
        """
        Close room.
        """
        self.clients = set()
        self.application = None

    def __eq__(self, other):
        if not isinstance(other, Room):
            return NotImplemented

        return self.application == other.application and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<Room %r @ %r (%d)>" % (self.name, self.application, len(self.clients))

    def enter(self, client):
        """
        Client enters room.

        @param client: room client
        @type client: L{RTMPServerProtocol}
        """
        assert client not in self.clients

        self.clients.add(client)

    def leave(self, client):
        """
        Client leaves room.

        @param client: room client
        @type client: L{RTMPServerProtocol}
        """
        assert client in self.clients

        self.clients.remove(client)

        if not self.clients:
            self.application.room_empty(self)

    def __iter__(self):
        """
        Iterate over clients.
        """
        return self.clients.__iter__()

    def empty(self):
        """
        Is this room empty?

        @rtype: C{bool}
        """
        return False if self.clients else True


