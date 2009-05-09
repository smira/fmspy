# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Base application class.
"""

import ConfigParser

from zope.interface import implements

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

        del self.rooms[room.name]
        room.dismiss()

    def name(self):
        """
        Get application name.

        @rtype: C{str}
        """
        return self.__class__.__name__

    def enabled(self):
        """
        Is application enabled or not?

        @rtype: C{bool}
        """
        try:
            return config.getboolean(self.name(), 'enabled')
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
