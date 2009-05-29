# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Example chat application.

U{http://localhost:3000/examples/chat/}
"""

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log

from fmspy.application import Application

class ChatApplication(Application):
    """
    Example application: chat.

    Basic chatting between clients.
    """
    implements(IPlugin)

    def invoke_identify(self, protocol, name):
        """
        Handler for C{identify(name)}.

        Client identifies himself in chat.
        """
        if hasattr(protocol._app, 'name'):
            #this connection was already identified
            raise Status(code="Chat.Error.AlreadyIdentified", level="error", description="Client was already identified")

        protocol._app.name = name

        for client in protocol._app.room:
            client.invoke('message', u'<%s> is entering chat...' % protocol._app.name)
        return None

    def invoke_say(self, protocol, text):
        """
        Handler for C{say(text)}.

        Client wants to say something in the chat.
        """
        if not hasattr(protocol._app, 'name'):
            #this connection wasn't identified yet
            raise Status(code="Chat.Error.NotIdentified", level="error", description="Client wasn't identified, please don't say anything")

        text = u'<%s>: %s' % (protocol._app.name, text)

        for client in protocol._app.room:
            client.invoke('message', text)

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
        for client in protocol._app.room:
            if client is not protocol:
                client.invoke('message', u'<%s> is leaving chat...' % getattr(protocol._app, 'name', 'Unknown'))
    
app = ChatApplication()
