.. FMSPy - Copyright (c) 2009 Andrey Smirnov.
   See COPYRIGHT for details.

============
User's Guide
============

.. index:: features

FMSPy aims to support subset of RTMP protocol and Flash Media Server features to be usable as:

 * audio/video streaming solution with clustering;
 * platform for online game development;
 * proxy for Flash clients, converting RTMP protocol into any other form, for example JSON-RPC over HTTP;
 * ...

FMSPy is written in Python language using Twisted Framework. Its RTMP protocol implementation could be used
in other Twisted-based projects.

FMSPy is open-source project under :ref:`MIT License <license>`.

Features
========

FMSPy is under active development at the moment, so features may change. 

RTMP Protocol
-------------

RTMP protocol implementation is stable. It supports handshake phase, packet reading/writing, slicing
into chunks and combining packet from chunks. More attention is given to server protocol, 
but client RTMP is under development.

Following packets are supported (decoding and encoding):

 * BytesRead
 * Ping
 * Invoke

FMSPy Application Server
------------------------

 * applications as plugins;
 * application connect/disconnect/room create/enter/etc. hooks;
 * application contains default room and set of named rooms;
 * iteration over clients of one room;
 * invoke handling at application level (RPC).

Installation
============

Using easy_install
------------------

FMSPy is easy installable::

    easy_install fmspy



From source code
----------------

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
