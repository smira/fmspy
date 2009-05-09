# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
FMSPy Twisted plugin.
"""

import sys

from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.python import usage, log
from twisted.plugin import IPlugin

class Options(usage.Options):
    optParameters = [
                        ["rtmp-port", None, 1935, "RTMP port"],
                        ["rtmp-interface", None, '', "RTMP bind address"],
                    ]


class FMSPyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "fmspy"
    description = "Flash Media Server written in Python"
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        observer = log.FileLogObserver(sys.stderr)
        log.addObserver(observer.emit)

        from fmspy.config import config
        
        if options['rtmp-port'] != 1935:
            config.set('RTMP', 'port', options['rtmp-port'])
        if options['rtmp-interface'] != '':
            config.set('RTMP', 'interface', options['rtmp-interface'])

        from twisted.application import internet, service
        from fmspy.rtmp.protocol import RTMPServerFactory

        s = service.MultiService()

        h = internet.TCPServer(config.getint('RTMP', 'port'), RTMPServerFactory(), config.getint('RTMP', 'backlog'), config.get('RTMP', 'interface'))
        h.setServiceParent(s)

        from fmspy.application import app_factory

        def appsLoaded(_):
            log.msg("Applications loaded.")

        def appsError(fail):
            log.err(fail, "Applications failed to load.")

        app_factory.load_applications().addCallbacks(appsLoaded, appsError)

        log.removeObserver(observer.emit)

        return s

# Now construct an object which *provides* the relevant interfaces

# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = FMSPyServiceMaker()
