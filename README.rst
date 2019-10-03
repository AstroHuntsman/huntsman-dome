Huntsman Telescope dome control
===============================

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

Code to run the Huntsman Telescope dome control hardware

Overview
--------

The Huntsman Telescope dome control software has two components,
one written in C++ the other in python.

The C++ component is a X2Dome driver that interfaces with TheSkyX
and passes commands through to the python component. This is done
using the `gRPC <https://grpc.io/>`_ framework, allowing the C++
component to pass information to the python component.

The python component is implemented on a raspberry pi that controls
the dome rotation motor. It controls the activation of the motor
and tracks the dome position using an encoder. It returns information
(such as dome position) to the C++ component using gRPC as well.

The C++ code is built around Software Bisque's X2 standard. For more
infomation on this `see here <https://www.bisque.com/x2standard/class_x2_dome.html#a7ffd792950cdd0abe1b022e7a8caff9e>`.

HOW TO RUN THE STUPID THING
===========================

For installation of dependencies/instructions for compiling and installing the
required TheSkyX driver see sections below. Assuming everything is set up
correctly, this is how you would set up the dome control system.

* Navigate to the directory containing the gRPC python server file
* ``$ cd huntsman-dome/domehunter/gRPC-server/``
* Use the -h flag to get information on the available command line flags
* ``$ python hx2dome.proto_server.py -h``
* To run server in simulated hardware mode run with the -s flag
* ``$ python hx2dome.proto_server.py -s``
* Now the server is running, you may start TheSkyX
* Within TheSkyX go to the Dome Setup menu and select the Huntsman Telescope
* Open TheSkyX log window and place by the python server window to watch for activity/status messages



C++/gRPC Component
==================

Requirements
------------

``grpc python`` For reference see `here <https://grpc.io/docs/quickstart/python/>`_.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------

To install (on MacOS or Linux) the required grpc python packages run the following::

  $ python -m pip install --upgrade pip
  $ python -m pip install grpcio
  $ python -m pip install grpcio-tools


``grpc C++`` For reference see `here <https://grpc.io/docs/quickstart/cpp/>`_.
------------------------------------------------------------------------------------------------------------------------------------------------------------

Detailed instructions to install from source on any OS can be found `here <https://github.com/grpc/grpc/blob/master/BUILDING.md>`_.

For convenience a summary of the required steps is given below.

To install dependencies for a linux OS, run the following::

  $ [sudo] apt install build-essential autoconf libtool pkg-config
  $ [sudo] apt install libgflags-dev libgtest-dev
  $ [sudo] apt install clang libc++-dev

To do the same on MacOS (with homebrew installed), run::

  $ [sudo] xcode-select --install
  $ brew install autoconf automake libtool shtool
  $ brew install gflags

Now to build grpc from source on Linux or MacOS run the following::

  $ cd /usr/local/bin/
  $ git clone -b $(curl -L https://grpc.io/release) https://github.com/grpc/grpc
  $ cd grpc/
  $ git submodule update --init
  $ make
  $ make install
  $ cd third_party/protobuf/
  $ git submodule update --init --recursive
  $ ./autogen.sh
  $ ./configure
  $ make
  $ make check
  $ make install


Alternatively to installing from source, you can install via homebrew on MacOS by running::

  $ brew tap grpc/grpc
  $ brew install -s -- --with-plugins grpc
  $ brew install protobuf
  $ brew install protobuf-c

The homebrew installation method has been tested on MacOS HighSierra. However,
If problems occur during compilation (missing header files etc) you might want
to try installing from source.

Compiling TheSkyX Driver
------------------------

The files for compilation and installation are found in the
``domehunter/gRPC-TheSkyX-driver/`` directory. The relevant files are;


* ``domelistHuntsmanDome.txt``
* ``TheSkyX_plugin_[MAC,LINUX]_install.sh``
* ``Makefile_[MAC,LINUX]``

The first two are files are used to install the compiled C++
driver into TheSkyX application directory.

|

In order to compile the driver simply run the makefile recipe for your OS (LINUX/MAC)::

  $ cd domehunter/gRPC-TheSkyX-driver/
  $ make -f Makefile_LINUX

This will produce a ``.so`` file in the ``domehunter/gRPC-TheSkyX-driver/``
directory for Linux and a ``.dylib`` file for Mac. This file, as well as the
``domelistHuntsmanDome.txt`` file need to be copied into TheSkyX application
directory. This can be done by running the installation script::

  $ . TheSkyX_LINUX_plugin_install.sh

Replace `LINUX` with `MAC` if installing on a MacOS system and vice versa.

|

Once the driver is installed in TheSkyX, it can be selected from
the dome selection menu. Before issuing any commands, start the
``domehunter/gRPC-server/hx2dome.proto_server.py`` in a new terminal.
When you issue a command through TheSkyX, the C++ driver will send
a remote procedure call through to the gRPC python server.

The gRPC python server can be run in a communication test mode that doesn't
require any hardware. It will simply return dummy messages back to the TheSkyX
driver. To get help with running the server (in normal or testing mode etc),
run the following command in terminal::

  $ cd domehunter/gRPC-server/
  $ python hx2dome.proto_server.py -h

gRPC automatically generated files
----------------------------------

In the ``domehunter/gRPC-TheSkyX-driver/`` directory there are a number
of shell scripts. These can be used to generate the gRPC files within
the ``domehunter/gRPC-TheSkyX-driver/src/`` directory. These scripts contain
path variables that may need to be adjusted to your local machine. You
shouldn't need to worry about  this as the generated files are committed to
the repository and shouldn't need to be generated (I think...?).

The code for the Huntsman dome driver is contained in the
``domehunter/gRPC-TheSkyX-driver/src`` directory. The code for the gRPC
server that runs on the raspberryPi is contained in the
``domehunter/gRPC-server/`` directory. These directories contain
both human written files and files automatically generated by gRPC
tools. The human written files are,

* ``main.cpp`` - establishes main library to X2 driver (mostly copy/paste from example)
* ``main.h`` - header for main.cpp
* ``x2dome.cpp`` - the library code that serves the RPC from TSX to python server
* ``x2dome.h`` - header for x2dome.cpp
* ``hx2dome.proto`` - language agnostic RPC definitions used by everthing
* ``hx2dome.proto_server.py`` - python server that receives RPC from TSX

The remaining cpp and python files are automatically produced
by gRPC and shouldn't need to be looked at. If for some reason
you want to generate these files yourself, you can use the following shell
scripts::

$ domehunter/gRPC-TheSkyX-driver/generate_grpc_cpp_code.sh
$ domehunter/gRPC-server/generate_grpc_python_code.sh


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

Tests
-----
In order to run the test suite, go to the source direction (``huntsman-dome/``)
and run the following command::

  $ python setup.py test --coverage

Which will produce a coverage report in ``huntsman-dome/htmlcov``


License
-------

This project is Copyright (c) Huntsman Team and licensed under
the terms of the BSD 3-Clause license. This package is based upon
the `Astropy package template <https://github.com/astropy/package-template>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.
