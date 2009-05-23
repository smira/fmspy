.. FMSPy - Copyright (c) 2009 Andrey Smirnov.
   See COPYRIGHT for details.

FMSPy - Flash Media Server written in Python
============================================

`FMSPy <http://fmspy.org/>`_ provides implementation of RTMP protocol upon `Twisted Framework <http://twistedmatrix.com/>`_.
On top of protocol implementation it builds server for Flash/Flex/Haxe/... clients. 

At the moment FMSPy supports:

 - basic RPC support;
 - application plugin infrastructure (applications are designed as FMSPy plugins);
 - application API.

`Plans <http://fmspy.org/roadmap/>`_ include:

 - live webcam audo/video streaming;
 - streaming from disk and writing streams to disk;
 - shared object support;
 - monitoring and load analysis;
 - clustering.

Plugin applications may use full power of Twisted, for example: memcached protocol, database
connections, RPC-over-HTTP, object persistence etc.

Contents:

.. toctree::
   :maxdepth: 2

   userguide
   developer

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

