# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
Tests for L{fmspy.application.application}.
"""

from twisted.trial import unittest

from fmspy.application.application import Application
from fmspy.application.room import Room
from fmspy.application.tests.test_room import ClientMock
from fmspy.config import config

class TestApplication(Application):
    """
    Test application.
    """

    def __init__(self):
        super(TestApplication, self).__init__()
        self._callLog = []

    def appConnect(self, protocol, path):
        self._callLog.append(('appConnect', protocol, path))

    def appCreateRoom(self, protocol, room_name, path):
        self._callLog.append(('appCreateRoom', protocol, room_name, path))
    
    def appEnterRoom(self, protocol, room, path):
        self._callLog.append(('appEnterRoom', protocol, room, path))

    def appLeaveRoom(self, protocol, room):
        self._callLog.append(('appLeaveRoom', protocol, room))
    
    def appDestroyRoom(self, room):
        self._callLog.append(('appDestroyRoom', room))


class ApplicationTestCase(unittest.TestCase):
    """
    Testcase for L{fmspy.application.application.Application}.
    """

    def setUp(self):
        self.a = TestApplication()
        config.add_section('TestApplication')
        config.set('TestApplication', 'name', 'test')

        self.c1 = ClientMock()
        self.c2 = ClientMock()

    def tearDown(self):
        config.remove_option('TestApplication', 'name')
        config.remove_option('TestApplication', 'enabled')
        config.remove_section('TestApplication')

    def test_name(self):
        self.failUnlessEqual('test', self.a.name())

    def test_enabled(self):
        self.failIf(self.a.enabled())
        config.set('TestApplication', 'enabled', 'yes')
        self.failUnless(self.a.enabled())

    def test_repr(self):
        self.failUnlessEqual("<TestApplication>", repr(self.a))

    def test_connect_hall(self):
        def checkIt(_):
            self.failUnlessEqual({}, self.a.rooms)
            self.failUnlessEqual([self.c1], list(self.a.hall))
            self.failUnlessIdentical(self.a.hall, self.c1._app.room)
            self.failUnlessEqual([
                    ('appConnect', self.c1, []),
                    ('appEnterRoom', self.c1, self.a.hall, []),
                            ], self.a._callLog)

        return self.a.connect(self.c1, []).addCallback(checkIt)

    def test_connect_room(self):
        def checkIt(_):
            self.failUnless(self.a.hall.empty())
            self.failUnlessEqual(['kitchen'], self.a.rooms.keys())
            self.failUnlessEqual([self.c1], list(self.a.rooms['kitchen']))
            self.failUnlessEqual([
                    ('appConnect', self.c1, ['kitchen', 'param']),
                    ('appCreateRoom', self.c1, 'kitchen', ['param']),
                    ('appEnterRoom', self.c1, self.a.rooms['kitchen'], ['param']),
                            ], self.a._callLog)

        return self.a.connect(self.c1, ['kitchen', 'param']).addCallback(checkIt)

    def test_connect_rooms(self):
        def checkIt(_):
            self.failUnless(self.a.hall.empty())
            self.failUnlessEqual(['kitchen'], self.a.rooms.keys())
            self.failUnlessEqual(sorted([self.c1, self.c2]), sorted(list(self.a.rooms['kitchen'])))
            self.failUnlessEqual([
                    ('appConnect', self.c1, ['kitchen']),
                    ('appCreateRoom', self.c1, 'kitchen', []),
                    ('appEnterRoom', self.c1, self.a.rooms['kitchen'], []),
                    ('appConnect', self.c2, ['kitchen']),
                    ('appEnterRoom', self.c2, self.a.rooms['kitchen'], []),
                            ], self.a._callLog)

        return self.a.connect(self.c1, ['kitchen']) \
                .addCallback(lambda _: self.a.connect(self.c2, ['kitchen'])) \
                .addCallback(checkIt)

    def test_connect_rooms2(self):
        def checkIt(_):
            self.failUnless(self.a.hall.empty())
            self.failUnlessEqual(['garage', 'kitchen'], sorted(self.a.rooms.keys()))
            self.failUnlessEqual([self.c1], list(self.a.rooms['kitchen']))
            self.failUnlessEqual([self.c2], list(self.a.rooms['garage']))
            self.failUnlessEqual([
                    ('appConnect', self.c1, ['kitchen']),
                    ('appCreateRoom', self.c1, 'kitchen', []),
                    ('appEnterRoom', self.c1, self.a.rooms['kitchen'], []),
                    ('appConnect', self.c2, ['garage']),
                    ('appCreateRoom', self.c2, 'garage', []),
                    ('appEnterRoom', self.c2, self.a.rooms['garage'], []),
                            ], self.a._callLog)

        return self.a.connect(self.c1, ['kitchen']) \
                .addCallback(lambda _: self.a.connect(self.c2, ['garage'])) \
                .addCallback(checkIt)

    def test_disconnect_hall(self):
        def checkIt(_):
            self.failUnlessEqual({}, self.a.rooms)
            self.failUnlessEqual([], list(self.a.hall))
            self.failUnlessEqual([
                    ('appConnect', self.c1, []),
                    ('appEnterRoom', self.c1, self.a.hall, []),
                    ('appLeaveRoom', self.c1, self.a.hall),
                            ], self.a._callLog)

        return self.a.connect(self.c1, []) \
                .addCallback(lambda _: self.a.disconnect(self.c1)) \
                .addCallback(checkIt)

    def test_disconnect_room(self):
        def checkIt(_):
            self.failUnlessEqual({}, self.a.rooms)
            self.failUnlessEqual([], list(self.a.hall))
            self.failUnlessEqual([
                    ('appConnect', self.c1, ['kitchen']),
                    ('appCreateRoom', self.c1, 'kitchen', []),
                    ('appEnterRoom', self.c1, Room(None, 'kitchen'), []),
                    ('appLeaveRoom', self.c1, Room(None, 'kitchen')),
                    ('appDestroyRoom', Room(None, 'kitchen')),
                            ], self.a._callLog)

        return self.a.connect(self.c1, ['kitchen']) \
                .addCallback(lambda _: self.a.disconnect(self.c1)) \
                .addCallback(checkIt)

    def test_disconnect_room2(self):
        def checkIt(_):
            self.failUnlessEqual(['kitchen'], self.a.rooms.keys())
            self.failUnless(self.a.hall.empty())
            self.failUnlessEqual([self.c2], list(self.a.rooms['kitchen']))

        return self.a.connect(self.c1, ['kitchen']) \
                .addCallback(lambda _: self.a.connect(self.c2, ['kitchen'])) \
                .addCallback(lambda _: self.a.disconnect(self.c1)) \
                .addCallback(checkIt)

    def test_refuse_connect(self):
        def refuseConnect(room, path):
            assert False
        self.a.appConnect = refuseConnect

        def checkIt(_):
            self.failUnlessEqual({}, self.a.rooms)
            self.failUnlessEqual([], list(self.a.hall))
            self.failUnlessEqual([], self.a._callLog)

        return self.a.connect(self.c1, ['kitchen']) \
                .addCallbacks(lambda _: self.failUnless(False), lambda fail: fail.trap(AssertionError)) \
                .addCallback(checkIt)

    def test_refuse_create_room(self):
        def refuseCreate(protocol, room_name, path):
            assert False
        self.a.appCreateRoom = refuseCreate

        def checkIt(_):
            self.failUnlessEqual({}, self.a.rooms)
            self.failUnlessEqual([self.c2], list(self.a.hall))
            self.failUnlessEqual([
                    ('appConnect', self.c2, []),
                    ('appEnterRoom', self.c2, self.a.hall, []),
                    ('appConnect', self.c1, ['kitchen']),
                ], self.a._callLog)

        return  self.a.connect(self.c2, []) \
                .addCallback(lambda _: self.a.connect(self.c1, ['kitchen'])) \
                .addCallbacks(lambda _: self.failUnless(False), lambda fail: fail.trap(AssertionError)) \
                .addCallback(checkIt)

    def test_refuse_enter_room(self):
        def refuseEnter(protocol, room, path):
            assert False
        self.a.appEnterRoom = refuseEnter

        def checkIt(_):
            self.failUnlessEqual({}, self.a.rooms)
            self.failUnlessEqual([], list(self.a.hall))
            self.failUnlessEqual([
                    ('appConnect', self.c1, ['kitchen']),
                    ('appCreateRoom', self.c1, 'kitchen', []),
                    ('appDestroyRoom', Room(self.a, 'kitchen')),
                ], self.a._callLog)

        return  self.a.connect(self.c1, ['kitchen']) \
                .addCallbacks(lambda _: self.failUnless(False), lambda fail: fail.trap(AssertionError)) \
                .addCallback(checkIt)
