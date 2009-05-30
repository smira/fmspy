.. FMSPy - Copyright (c) 2009 Andrey Smirnov.
   See COPYRIGHT for details.

============
User's Guide
============

FMSPy aims to support subset of RTMP protocol and Flash Media Server features to be usable as:

 * audio/video streaming solution with clustering;
 * platform for online game development;
 * proxy for Flash clients, converting RTMP protocol into any other form, for example JSON-RPC over HTTP;
 * ...

FMSPy is written in Python language using Twisted Framework. Its RTMP protocol implementation could be used
in other Twisted-based projects.

FMSPy is open-source project under :ref:`MIT License <license>`.

.. index::
   pair: FMSPy; features

Features
========

FMSPy is under active development at the moment, so features may change. 

.. index::
   triple: FMSPy; features; RTMP

RTMP Protocol
-------------

RTMP protocol implementation is stable. It supports handshake phase, packet reading/writing, slicing
into chunks and combining packet from chunks. More attention is given to server protocol, 
but client RTMP is under development.

Following packets are supported (decoding and encoding):

 * BytesRead
 * Ping
 * Invoke

.. index::
   triple: FMSPy; features; applications

FMSPy Application Server
------------------------

 * applications as plugins;
 * application connect/disconnect/room create/enter/etc. hooks;
 * application contains default room and set of named rooms;
 * iteration over clients of one room;
 * invoke handling at application level (RPC).

.. _installation:
.. index::
   pair: FMSPy; installation

Installation
============

Requirements
------------
  
 * Python 2.5+ (maybe could work with tweaks under 2.4)
 * UNIX (Linux, BSD) operating system, could work under Windows, not tested

Using easy_install
------------------

FMSPy is easy installable::

    easy_install fmspy

Easy_install should automatically install all required dependencies, usually
setuptools (easy_install) come preinstalled in all major Linux distros.

From source code
----------------

Perform source code checkout::
  
    git clone http://fmspy.org/git/ fmspy

From this checkout run::

    python setup.py build
    python setup.py install

Requirements:
    
    * Twisted 8.1.0+ (http://twistedmatrix.com/)
    * PyAMF 0.4+ (http://pyamf.org/)

.. _running:

Running
=======

FMSPy is a ``twistd`` plugin, so startup is flexible and easy. For non-daemon mode (debug, console)::

    twistd -n fmspy

Use ``Ctrl+C`` to stop server.

If you want to daemonize FMSPy, perform log rotation, pidfile handling, etc. please refer to 
`twistd documentation <http://twistedmatrix.com/projects/core/documentation/man/twistd-man.html>`_.

.. index::
   single: examples

Examples
========

Some examples are bundled with FMSPy distribution. After ref:`starting <running>` FMSPy server, point your browser
to http://localhost:3000/examples/. (Default port for web is 3000).

.. index::
   pair: examples; echotest

Echotest example
----------------

Echotest example is based on code from `Red5 <http://osflash.org/red5>`_ project. Flash sends different data types
as remote invokes (RPC) and waits for server to return the same value back. Example running time could be taken as
some measure of server performance and correctness.

.. index::
   pair: examples; chat

Chat example
------------

Chat application receives messages from clients and retransmits them to all clients connected to application room, so
server-side chat application code serves as example of some best practices in this area.

.. _config:

.. index::
   pair: configuration; file
   single: fmspy.cfg

Configuration file
==================

FMSPy configuration file is named :file:`fmspy.cfg` and it has INI-like syntax:

.. literalinclude:: ../../fmspy.cfg 
   :language: ini
   :lines: 5-

.. index::
   pair: configuration; RTMP

RTMP section
------------

This section specifies core configuration options for RTMP protocol.

.. index::
   triple: configuration; RTMP; handshakeTimeout

``handshakeTimeout`` (*int*)
    Timeout for full handshake operation. From TCP connection time to end of handshake should
    pass no more than ``handshakeTimeout`` seconds.

.. index::
   triple: configuration; RTMP; port

``port`` (*int*)
    TCP port to listen on for incoming RTMP connections (1935 is standard port for RTMP).
    If port is 1935, URL for connection looks like: ``rtmp://localhost/``, if port is
    different it should be specified explicitly: ``rtmp//localhost:2000/``. For firewall traversal
    sometimes it is OK to start FMSPy on port 80, for example.

.. index::
   triple: configuration; RTMP; interface

``interface`` (*str*)
    Interface name (IP) to listen for incoming connections. If ``interface`` is empty, FMSPy
    will listen on all available interfaces.

.. index::
   triple: configuration; RTMP; backlog

``backlog`` (*int*)
    Backlog for incoming connections, should be raised on busy servers. See manual page for ``accept(2)`` for
    more information.

.. index::
   triple: configuration; RTMP; pingInterval

``pingInterval`` (*int*)
    If ``pingInterval`` seconds passes after last received byte, FMSPy sends Ping packet to other
    side of RTMP conversation. 

.. index::
   triple: configuration; RTMP; keepAliveTimeout

``keepAliveTimeout`` (*int*)
    If FMSPy doesn't receive any data during ``keepAliveTimeout`` seconds, it assumes connection
    is broken and closes it. Actually, ``keepAliveTimeout`` should be more than ``pingInterval``. 
    After ``pingInterval`` seconds of inactivity FMSPy sends Ping packet, other side should repy
    with Pong, and ``keepAliveTimeout`` is reset.

.. index::
   pair: configuration; HTTP

HTTP section
------------

In this section bundled HTTP server is configured (it is not critical to basic FMSPy operation).

.. index::
   triple: configuration; HTTP; enabled

``enabled`` (*bool*)
    If HTTP server is disabled, other options in this section don't make sense.

.. index::
   triple: configuration; HTTP; port

``port`` (*int*)
    HTTP port to listen for incoming connections.

.. index::
   triple: configuration; HTTP; examples-enabled
   single: examples

``examples-enabled`` (*bool*)
    If true, FMSPy examles are bound to ``/examples/`` url of HTTP server. Not
    recommended for production environments.

Application section
-------------------

There could be many application sections for each FMSPy application. Section is named after
application plugin class, for example application ``EchoApplication`` section is ``EchoApplication``.
Every application should be enabled explicitly in config file (by default, each application is disabled).

``enabled`` (*bool*)
    Is application enabled?

``name`` (*str*)
    Name of application for RTMP url. Application entry point is mapped to ``rtmp://host/name``. 

This section may contain other application-specific options.

FAQ
===

*Is this program really free?*
  Yes.

*Is this program open-source?*
  Yes.

*What language/framework was used?*
  Python/Twisted Framework.

*How can I use it?*
  Every way you may imagine. It is under active development, but it could be used as basis of some bigger application for
  example. RPC is quite stable and working in this first release.

*Is it better than Adobe FMS?*
  FMSPy doesn't have as many features and options as Adobe FMS does. I suppose it should never will have so many features.
  FMSPy is simple, free, open-source. I will do my best to make it lightning fast, supporting big number of simultaneous
  connections, streaming, clustering etc.

*How does FMSPy compare to Red5?*
  Red5 is more featured, actually it's more like Adobe FMS. In my experience Red5 was quite unstable and unusable in 
  production environment under load, contained hard to track spurious bugs. 

*How does FMSPy compare to Milgra, RTMPy, etc...*
  These projects have almost same goals as FMSPy.

*What does it mean if I receive messages like* ``ConfigParser.NoSectionError: No section: 'RTMP'`` *?*
  Most likely FMSPy was unable to find its configuration file, :file:`fmspy.cfg`. FMSPy looks for configuration
  file at package install dir, :file:`/etc/fmspy.cfg`, :file:`/usr/local/etc/fmspy.cfg`  and in current directory
  (in that order).

.. _license:
.. index:: license

License
=======

FMSPy is licensed under terms of `MIT License <http://www.opensource.org/licenses/mit-license.php>`_:

Copyright (c) 2009 Andrey Smirnov (me@smira.ru)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
