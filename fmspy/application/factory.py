# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Application factory.

Loading application, dispatching control.
"""

from twisted.plugin import getPlugins
from twisted.python import log
from twisted.internet import defer

from fmspy.application.interfaces import IApplication
from fmspy.rtmp.constants import StatusCodes
import fmspy.plugins

class ApplicationNotFoundError(Exception):
    """
    Application not found in factory.
    """
    code = StatusCodes.NC_CONNECT_INVALID_APPLICATION

class ApplicationFactory(object):
    """
    Application factory holds all loaded applications.

    Factory can dispatch calls to applications.

    @ivar apps: loaded applications
    @type apps: C{dict}
    @ivar plugin_module: root module for application plugins
    @type plugin_module: C{module}
    """

    def __init__(self, plugin_module=None):
        """
        Construct factory.

        @param plugin_module: root module for application plugins, defaults to L{fmspy.plugins}.
        @type plugin_module: C{module}
        """
        self.plugin_module = plugin_module
        if self.plugin_module is None:
            self.plugin_module = fmspy.plugins
        self.apps = {}

    @defer.inlineCallbacks
    def load_applications(self):
        """
        Load all applications.

        @return: Deferred, fired on application load complete
        @rtype: C{Deferred}
        """
        for app in getPlugins(IApplication, self.plugin_module):
            if app.enabled():
                log.msg("Loading %r..." % app)
                try:
                    yield app.load()
                    assert app.name() not in self.apps
                except:
                    log.err(None, "Failed loading %r:" % app)
                    continue
                self.apps[app.name()] = app

                log.msg("Loaded %r @ %r." % (app, app.name()))

    def get_application(self, name):
        """
        Get application by name.

        @param name: application name
        @type name: C{str}
        @return: application
        @rtype: L{Application}
        """
        if name not in self.apps:
            raise ApplicationNotFoundError, name

        return self.apps[name]

factory = ApplicationFactory()

