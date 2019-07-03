#ifndef _MultiConnectionDeviceInterface_H
#define _MultiConnectionDeviceInterface_H

#define MultiConnectionDeviceInterface_Name "com.bisque.TheSkyX.MultiConnectionDeviceInterface/1.0"

class BasicStringInterface;


/*!
\brief This optional interface, MultiConnectionDeviceInterface, provides X2 implementors a way to make x2 drivers that support
the capacity to accept multiple connections simultaneously without error or conflict (such as multi-device hubs).

All x2 hardware devices, except cameras, can be made to work with the MultiConnectionDeviceInterface.  The MultiConnectionDeviceInterface is 
fairly generic solution and allows the sharing of any kinds of interfaces. A common use of this interface is to share a serial port between x2 drivers,
in which case the SerXInterface and it's corresponding IO MutexInterface (namely m_pSerX and m_pIOMutex typically found in x2 examples) are shared
between x2 drivers.  Sufficiently motivated and experienced developers should be able to use this to control any kind of shared multi-device interface between 
the same kind of devices or even with different devices.

Some concepts:
- All drivers contain a 'resource' of some kind that allows a connection to their device.
  Every instance of the driver that's created should have a copy of this resource.
- The first driver to establish a connection will have their resource copy become active.
  Subsequent instances of the driver will have inactive copies of the resource
- Drivers with inactive resources will have a reference to the 'active' resource singleton for device interaction.
- While any drivers are connected, the active reference shall not be closed nor destroyed.  TheSkyX will ensure this
  by directing the driver holding the active resource to 'trade' it with a driver instance that's remaining active
  before the link is terminated.
- This interface leverages and is built on top of the standard LinkInterface which TheSkyX uses as a means to connect/disconnect from all x2 drivers.

Note, this interface is in use in the field and works for the Optec Lynx Focuser (LynxPlugIn, example code snippets below) where two focusers, one for imager, one for autoguider, 
share the same serial port, yet are implemented as two instances of the same dll as the imager focuser and the autoguider focuser in TheSkyX. 
 
Effectively this interface makes it possible for x2 drivers to share a pointer to a resource or resources between
x2 drivers. The LynxPlugIn shares the SerXInterface and MutexInterface but its not necessarily limited to those pointers nor
devices in kind (for example, a mount could share its usb connection with a focuser).

Keep in mind that TheSkyX will interface with this driver across different threads, so take care that any calls into a connection resource
must be made thread-safe (usually by also sharing the IO MutexInterface as well).

Implementing this interface should only be attempted <b>after</b> successfully creating x2 drivers that properly work when connecting to
the resource standalone without sharing.  If the case where the driver is used stand alone doesn't function properly there is no possible way 
a MultiConnectionDeviceInterface implementation is going to work. In fact, the stand alone case will always be the place to turn
when trouble shooting any problems with this interface.  IOW, get the two or more x2 drivers to work stand alone without this interface, and
then a MultiConnectionDeviceInterface implementation will work identially except sharing the desired resource(s).  When implementing
this interface for the case of sharing a serial port, basically the correct m_pSerX and m_pIOMutex are put inplace (almost) tranparently to 
the x2 driver.

For this interface to function, TheSkyX build 6812 or later released Thursday March 21, 2013 is required.  Earlier builds simply ignore
this interface and sharing resoures is not possible.

See TheSkyXFacadeForDriversInterface::build() to determine the build of TheSky in use an act accordingly based on your requirements. 

\ingroup Interface

*/
class MultiConnectionDeviceInterface
{
protected:
	int m_nInstanceCount;

public:
	/*!Since drivers implementing this interface behave like "normal" (they don't share a resource) when m_nInstanceCount is 1, this default
	   constructor allows earlier builds of TSX to run these drivers even if the actual interface isn't implemented.*/
	MultiConnectionDeviceInterface()
	{
		m_nInstanceCount = 1;
	}

	/*!Implementors should return a string identifier unique to this specific physical device or known connection sharing setup.  
	   If multiple instances of the driver are in use, drivers that return identical identifiers will be treated as if they
	   represent connections to the same physical device.  Drivers returning different identifier strings will
	   continue to be treated as separate pieces of hardware. 

	   Drivers also implementing SerXInterface will additionally be checked by TheSkyX to see if they share the same
	   serial port (or TCP/IP address and port combination) or not and act accordingly.

	   Here is example code from the LynxPlugIn driver: 
	   \snippet lynxplugin.cpp deviceIdentifier

	   */
	virtual int deviceIdentifier(BasicStringInterface &sIdentifier) = 0;


	/*! TheSkyX will call this function once immediately before LinkInterface::establishLink(), then again any time the number of
	   drivers connecting to the same physical device as this one changes.  If this is the first driver connecting
	   to the device, nInstanceCount will be 1.  No driver will ever see a '0' value. 

	   This function can be implemented in order to perform any additional initialization that may be necessary
	   when the first connection is established.
   */
	virtual int setInstanceCount(const int &nInstanceCount)
	{
		m_nInstanceCount = nInstanceCount;
		return 0;
	}

	/*! Although some devices may support multiple connections, they may not support them in unlimited numbers.  TheSkyX will
	   call this function before a connection attempt is made to allow the driver to determine if it will be able to successfully attach
	   to the shared resource.
	   
	   For example, a camera/filter wheel combination device may support one camera connection and one filter wheel
	   device simultaneously.  If the peer array already contains both a camera and a filter wheel, bConnectionPossible should be set to false.

	   Here is example code from the LynxPlugIn driver: 
	   \snippet lynxplugin.cpp isConnectionPossible
	   */
	virtual int isConnectionPossible(const int &nPeerArraySize, MultiConnectionDeviceInterface **ppPeerArray, bool &bConnectionPossible) = 0;

	/*!
	If the driver determines that a connection is possible, TheSkyX will call this function tell the driver which of its peers
	holds the resource that should be used to connect.  pPeer will be equal to the 'this' pointer for the first driver to connect. 

	Here is example code from the LynxPlugIn driver: 
	\snippet lynxplugin.cpp useResource
	*/
	virtual int useResource(MultiConnectionDeviceInterface *pPeer) = 0;

	/*! 
	TheSkyX will call this function on the driver controlling the active resource immediately before the driver is disconnected.  The
    driver should 'swap' its (active) resource with the inactive one held by its peer.  In this way, the active resource may remain
    active without interruption when this instance's link is terminated. 
	Here is example code from the Lynx driver: 
	\snippet lynxplugin.cpp swapResource
   */
	virtual int swapResource(MultiConnectionDeviceInterface *pPeer) = 0;
};

#endif
