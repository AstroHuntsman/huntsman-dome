######################################################################
# Automatically generated by qmake (2.01a) Mon Aug 23 13:18:26 2010
######################################################################

TEMPLATE = lib
TARGET = x2dome
DEPENDPATH += .
INCLUDEPATH += .

CONFIG += dll

win32:		DEFINES += SB_WIN_BUILD
macx:		DEFINES += SB_MAC_BUILD
linux-g++:	DEFINES += SB_LINUX_BUILD

# Input
HEADERS += main.h \
           x2dome.h \
           ../../licensedinterfaces/basicstringinterface.h \
           ../../licensedinterfaces/sberrorx.h
SOURCES += main.cpp x2dome.cpp
