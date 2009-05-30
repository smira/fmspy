.. FMSPy - Copyright (c) 2009 Andrey Smirnov.
   See COPYRIGHT for details.

=================
Developer's Guide
=================

FMSPy allows easy extension via plugins. Application plugins represent new application functionality
built on top of core FMSPy RTMP features. Applications interact with Flash/Flex clients by means
of RPC, Shared Objects, streaming operations, etc.

Application example
===================

Let's develop sample FMSPy application. We assume that Python, Twisted, FMSPy is already :ref:`installed <installation>` on development
system.

At first, we need to design new plugin. FMSPy uses `plugin subsystem from Twisted <http://twistedmatrix.com/projects/core/documentation/howto/plugin.html>`_.
Let's name our application *Foo*. We choose some source directory and create our application folder structure::

   fmspy/
     plugins/
       foo_plugin.py

.. note::
    There's no ``__init__.py`` in ``fmspy/plugins``. It isn't required and should be avoided. 


Minimal plugin code looks like this:

.. code-block:: python
    :linenos:

    from zope.interface import implements
    from twisted.plugin import IPlugin

    from fmspy.application import Application

    class FooApplication(Application):
        implements(IPlugin)

    app = FooApplication()

Here we derive our ``ChatApplication`` class from class :class:`Application`, which is base class for all FMSPy applications. 
Our class should implement ``IPlugin`` interface, so that Twisted plugin subsystem knows that it is a plugin. We should
instanciate our class in any global variable of plugin module, like it is done on line 9 of example.

Next, we must enable application in :ref:`configuration file <config>`:

.. code-block:: ini

    [FooApplication]
    enabled = yes
    name = foo

Path to ``fmspy`` folder of our Foo application should be in ``PYTHONPATH`` environment variable: it could be put there
explicitly or just start FMSPy in directory with ``fmspy`` (current directory is searched for modules).

Next, we start FMSPy server. It should find our ``foo_plugin.py`` and load it::

    $ twistd -n fmspy
    2009-05-30 18:24:38+0400 [-] RTMP server at port 1935.
    2009-05-30 18:24:39+0400 [-] Loading <FooApplication>...
    2009-05-30 18:24:39+0400 [-] Loaded <FooApplication> @ 'foo'.

Now flash clients should successfully connect to *Foo* with URL: ``rtmp://localhost/foo``. In order to enter room ``kitchen``
at *Foo* use URL: ``rtmp://localhost/foo/kitchen``.

Reference
=========

Classes
-------

.. class:: Application

   Base class for all applications in FMSPy. Every application extends this class, overriding
   some methods. 

   Each enabled application class is instantiated on server startup. So, each application object
   may contain state shared between application clients.

   Application collects connected clients in *rooms*. Every application has *root* room, called *hall*.
   Hall is unnamed, client enters this room if room name isn't given in connect URL. If room name
   is given (``rtmp://host/app/room``), client is directed to room with that name.


.. class:: Room

   Room is a collection of clients, it is application context associated with some clients.
   Room may contain some FMSPy objects: streams, shared objects, ...

   Room is iterable (iterates over its clients).

Application class
-----------------

.. method:: Application.load(self)

   This method is called on application startup. 

   Application may initialize database connections, load external resources, etc.
    
   This method can result in ``Deferred``. Application startup is delayed
   until return from this method.

There are several overridable hooks that inform about client connect/disconnect:

.. method:: Application.appConnect(self, protocol, path)

        Client is connection to this application.

        Hook for custom application, may be deferred.

        If application wants to refuse client from connecting,
        it should raise some error.

.. method:: Application.appCreateRoom(self, protocol, room_name, path)

        Room is about to be created for new client.

        Hook for custom application, may be deferred.

        If application wants to refuse client from creating this room,
        it should raise some error. This method isn't called
        for root room (L{hall}), root room is created implicitly
        for every application.
        
    
.. method:: Application.appEnterRoom(self, protocol, room, path)

        Client is about to enter room.

        Hook for custom application, may be deferred.

        If application wants to refuse client from entering this room,
        it should raise some error.
        

.. method:: Application.appLeaveRoom(self, protocol, room)

        Client is leaving room.

        Hook for custom application, should return
        immediately. No exceptions should be raised
        in this method.

    
.. method:: Application.appDestroyRoom(self, room)

        Room is about to be destroyed (it became empty).

        Hook for custom application, should return
        immediately. No exceptions should be raised
        in this method.


