Huntsman Telescope dome control
===============================

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

Code to run the Huntsman Telescope dome control hardware

Overview
--------

The Huntsman Telescope dome control software has two components,
one written in c++ the other in python.

The C++ component is a X2Dome driver that interfaces with TheSkyX
and passes commands through to the python component. This is done
using the `gRPC <https://grpc.io/>`_ framework, allowing the c++
component to pass infomation to the python component.

The python component is implemented on a raspberry pi that controls
the dome rotation motor. It controls the activation of the motor
and tracks the dome position using an encoder. It returns infomation
(such as dome position) to the c++ component using gRPC as well.

The c++ code is built around Software Bisque's X2 standard. For more
infomation on this `see here <https://www.bisque.com/x2standard/class_x2_dome.html#a7ffd792950cdd0abe1b022e7a8caff9e>`.

C++/gRPC Component
==================

Requirements
---------------

``grpc python`` For reference see `here <https://grpc.io/docs/quickstart/python/>`_.

To install (on MacOS or Linux) the grpc python packages needed run the following::

  python -m pip install --upgrade pip
  python -m pip install grpcio
  python -m pip install grpcio-tools


``grpc c++`` For reference see `here <https://grpc.io/docs/quickstart/cpp/>`_.

Instructions to install from source on any OS can be found `here <https://github.com/grpc/grpc/blob/master/BUILDING.md>`_.

To install depedencies for a linux OS run the following::

  [sudo] apt-get install build-essential autoconf libtool pkg-config
  [sudo] apt-get install libgflags-dev libgtest-dev
  [sudo] apt-get install clang libc++-dev

To do the same on MacOS (with homebrew installed) run::

  [sudo] xcode-select --install
  brew install autoconf automake libtool shtool
  brew install gflags

Now to build grpc from source on Linux or MacOS run the following::

  cd /usr/local/bin/
  git clone -b $(curl -L https://grpc.io/release) https://github.com/grpc/grpc
  cd grpc/
  git submodule update --init
  make
  make install
  cd third_party/protobuf/
  git submodule update --init --recursive
  ./autogen.sh
  ./configure
  make
  make check
  make install


To install the above on OSX, run::

  brew tap grpc/grpc
  brew install -s -- --with-plugins grpc
  brew install protobuf
  brew install protobuf-c

However, this may require some editing of the driver makefiles. Specifically
the include and linking flags, as homebrew will place relevant files and
libraries in different locations to the installation from source method
outlined above. The makefiles are written with the installation from source
setup in mind.

Getting Started
---------------

The files for compilation and installation are found in the
``domehunter/protos/`` directory. The relevant files are,


* ``domelistHuntsmanDome.txt``
* ``TheSkyX_plugin_install.sh``
* ``Makefile``

The first two are files are used to install the compiled c++
driver. You should be able to simply run the shell script once
the driver is compiled and located in the ``domehunter/protos/``
directory, with filename ``libHuntsmanDome.so``.

|

In order to compile the driver simply run the makefile recipe for your OS (LINUX/MAC)::

  cd domehunter/protos/
  make -f Makefile_LINUX

This will produce a .so file in the protos directory for Linux and a .dylib file for Mac.
This file as well as the ``domelistHuntsmanDome.txt`` file need to be copied into TheSkyX
application directory. This can be done by running the installation script::

  . TheSkyX_LINUX_plugin_install.sh

Replace `LINUX` with `MAC` if installing on a MacOS system and vice versa.

|

Once the driver is installed in TheSkyX, it can be selected from
the dome selection menu. Before issuing any commands, start the
``domehunter/protos/src/hx2dome.proto_server.py`` in a new terminal.
When you issue a command through TheSkyX, the c++ driver will send
a remote procedure call through to the gRPC python server. Currently
the server will just return a dummy response to the c++ driver,
which will be passed to TheSkyX. In the future the gRPC python server
will be used to issue commands to the dome hardware.

gRPC automatically generated files
----------------------------------

In the ``domehunter/protos/`` directory there are a number of shell
scripts. These can be used to generate the gRPC files within the ``src/``
directory. These scripts contain path variables that may need to be
adjusted to your local machine. You shouldn't need to worry about
this as the generated files are committed to the repositry and
shouldn't need to be generated (I think...?).

The code for the Huntsman dome driver is contained in the
``domehunter/protos/src`` directory. This directory contains both
human written files and files automatically generated by gRPC
tools. The human written files are,

* ``main.cpp`` - establishes main library to X2 driver (mostly copy/paste from example)
* ``main.h`` - header for main.cpp
* ``x2dome.cpp`` - the library code that serves the RPC from TSX to python server
* ``x2dome.h`` - header for x2dome.cpp
* ``hx2dome.proto`` - language agnostic RPC definitions used by everthing
* ``hx2dome.proto_server.py`` - python server that receives RPC from TSX

The remaining cpp and python files are automatically produced
by gRPC and shouldn't need to be looked at. If for some reason
you want to generate these files yourself, see the
*gRPC automatically generated files* section below.


Python RaspberryPi Component
============================

Requirements
---------------
Required:

* ``gpiozero`` python library

Optional:

* ``smbus`` and ``sn3218`` python libraries

Note:

The ``smbus`` and ``sn3218`` are used to control the automationHAT status
LEDs. If you plan on running the code without the automationHAT these libraries
aren't required.

Getting Started
---------------
Follow the example jupyter notebook in the examples direction
(``dome_control_example``). The automationHAT hardware is not required to run the
code in testing mode.


License
-------

This project is Copyright (c) Huntsman Team and licensed under
the terms of the BSD 3-Clause license. This package is based upon
the `Astropy package template <https://github.com/astropy/package-template>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.
