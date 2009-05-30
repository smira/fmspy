#!/usr/bin/env python
#
# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

from setuptools import setup

setup(name='fmspy',
      version='0.1.0',
      description='Flash Media Server in Python using Twisted Framework',
      author='Andrey Smirnov',
      author_email='me@smira.ru',
      url='http://fmspy.org/',
      keywords='flash rtmp twisted fms',
      install_requires=['Twisted>=8.1.0', 'pyAMF>=0.4'],
      zip_safe=False,
      license='MIT',
      data_files=[('etc', ['fmspy.cfg']), ('share/examples/echotest', ['examples/echotest/index.html', 'examples/echotest/echo_test.swf']),
          ('share/examples/chat', ['examples/chat/index.html', 'examples/chat/chat.swf'])],
      include_package_data=True,
      long_description="""FMSPy provides implementation of RTMP protocol upon Twisted Framework.
On top of protocol implementation it builds server for Flash/Flex clients. 

At the moment FMSPy supports:
 - basic RPC support;
 - application plugin infrastructure (applications are designed as FMSPy plugins);
 - application API.

Plans include:
 - live webcam audo/video streaming;
 - streaming from disk and writing streams to disk;
 - shared object support;
 - monitoring and load analysis;
 - clustering.

Plugin applications may use full power of Twisted, for example: memcached protocol, database
connections, RPC-over-HTTP, object persistence etc.
""",
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Environment :: No Input/Output (Daemon)',
            'Framework :: Twisted',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Telecommunications Industry',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Operating System :: POSIX :: BSD',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.5',
            'Topic :: Communications',
            'Topic :: Internet',
            'Topic :: Multimedia :: Sound/Audio',
            'Topic :: Multimedia :: Video',
          ],
      packages=['fmspy', 
          'fmspy.application',
            'fmspy.application.tests',
          'fmspy.plugins', 
          'fmspy.rtmp', 
              'fmspy.rtmp.protocol', 
              'fmspy.rtmp.tests', 
          'twisted.plugins',
            ],
      )
