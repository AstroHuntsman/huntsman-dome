#ifndef _AsymmetricalEquatorialInterface_H
#define _AsymmetricalEquatorialInterface_H

#include "mounttypeinterface.h"

#define AsymmetricalEquatorialInterface_Name "com.bisque.TheSkyX.AsymmetricalEquatorialInterface/1.0"

/*!\defgroup Tool Device Driver Tool Kit*/
/*!\defgroup Driver Driver Interfaces */
/*!\defgroup Interface Optional Interfaces*/
/*!\defgroup Example Example Drivers*/
/*!\defgroup GUI Graphical User Interface (GUI)*/

/*! \page x2howto How to Write a TheSkyX Driver

	For illustration purposes, the following steps are for creation of a camera driver, but the same steps are involved in making any X2 driver.

	The X2Camera example source code provides a pattern to follow to create a TheSkyX camera driver.  

	-# Obtain TheSkyX version 10.1.9 or later.
	-# Tell TheSkyX A) how to display your camera to the user for selection and B) the name of the file that is your plug in binary by making your own company specific list of camera hardware.
		-# Make a copy of "cameralist.txt" distributed by TheSkyX and name it "cameralist My Company.txt" where 'My Company' is your company name.  The files goes in the same folder as cameralist.txt.
		-#	Edit "cameralist My Company.txt" remove all lines except one and by following the existing format, enter your specific camera information and the name of your plug in binary is "My Company Plug In File Name", for example:
			-# "2|My Company|My Company Hardware Model|Comment| |My Company Plug In File Name|x2 developer string||||"
			-# See the header of the file "hardwarelist.txt" distributed by TheSkyX for more details on this file format.
	-# Compile the X2Camera sample unmodified, and place the binary into the TheSkyX/Resources/Common/PlugIns/CameraPlugIns folder. Start TheSkyX, go to Telescope, Setup and in the Imaging System Setup tree select Cameras, select the X2Camera and choose Connect.  The X2 plug in dll CCEstablishLink will be called.
	-# Implement the X2Camera with device dependent io calls.  See the X2Camera source for more details on function calls.  Use conditional compilation for OS specific io calls or branch in main.cpp with two entirely different X2Camera implementations depending upon OS.

*/

/*! \page x2driverinstall Installing Your X2 Driver

	The x2 developer should provide a means to install/update their driver independent of TheSkyX.  For cross platform drivers, there is the need for a Windows/Mac installer.  
	Unfortunately, we are not aware of any good, free, cross platform installers (Installshield and bitrock are expensive). On Windows consider the MSI or nullsoft installer.
	
	At a minimum, your own x2 installer will need to distribute two files, your own "hardwarelist <Company Name>.txt" with your list of hardware and the corresponding plug in binary.  
	Any other libraries your binary requires also need distributed.  Please strive to minimize dependencies and static link libraries whenever possible.

	With the above being said, a vision Software Bisque is for TheSkyX to come with drivers (x2 or native) for the most popular hardware and for everything to work "out of the box."  
	IOW, install TheSkyX, and immediately control your dome, mount, camera, autoguider, filter wheel, focuser, rotator, etc, on either Windows and Mac.  This is another primary reason we've 
	architected x2 the way we did, to keep the x2 driver footprint small, efficient and with as few as possible dependencies.  If you have confidence in your x2 driver
	and are willing to stand behind it, TheSkyX's installer would love to include it, please contact Software Bisque to discuss.

	\section whereistheskyx Where Is TheSkyX Installed?

	There are many ways to find out where TheSkyX is installed.  TheSkyX has the following convention to hopefully make it easier to write an installer and works on both Mac and or Windows...

	Conventionally, TheSkyX 10.1.11 (build 4630 and later) provides a way for third parties easily find out where TheSkyX is installed.
	The file TheSkyXInstallPath.txt holds the path to where TheSkyX is installed.  TheSkyXInstallPath.txt file is found in the folder...

	on Windows: <Documents>/Software Bisque/TheSkyX Professional Edition

	on Mac: ~/Library/Application Support/Software Bisque/TheSkyX Professional Edition

	(For installations targeting TheSkyX Serious Astronomer Edition, replace the "TheSkyX Professional Edition" with "TheSkyX Serious Astronomer Edition" in the folder paths above.)

	Notes:
	- TheSkyX has to be run at least once before TheSkyXInstallPath.txt exists.
	- This convention is purposfully not dependent upon the Windows registry. 
	- TheSkyXInstallPath.txt is updated each time TheSkyX runs, so this convention still allows moving TheSkyX from one hard driver or folder to another. (Installsheild's HKLM\~\App\TheSkyX.exe registry convention is only written on install.)

	Here is a Windows script for determining the <Documents> folder:

	Set WshShell = Wscript.CreateObject("Wscript.Shell")<br>
	path=WshShell.RegRead("HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders\Personal")<br>
	MsgBox path<br>

*/

/*!	\page x2changelog Change Log

	- 1.01 - Changed x2mount example to use TheSkyXFacadeForDriversInterface instead of deprecated TheSkyXFacadeForMountsInterface (interface identical).
	- 1.02 - Added Mac make files for X2 examples.
	- 1.03 - The ModalSettingsDialogInterface and SerialPortParams2Interface are no longer mutually exclusive.
	- 1.04 - SerXInterface::open allows setting data bits.
	- 1.05 - Filter wheel support, see FilterWheelDriverInterface.
	- 1.06 - Documented \ref embeddeddevices.
	- 1.07 - Updated \ref x2driverinstall.
	- 1.08 - Made all x2 examples explicitly delete device driver tools (x2dome, x2filterwheel, x2mount, x2rotator did not). Published drivers should eventually follow suite to prevent a small memory leak when choosing different hardware.
	- 1.09 - Updated LoggerInterface documentation.
	- 1.10 - Documented and added X2Focuser example.
	- 1.11 - TrackingRatesInterface documentation update.
	- 1.13 - Updated documentation to use version 2 of the hardwarelist.txt (TheSkyX is backward compatible with version 1).
	- 1.14 - TrackingRatesInterface documentation update.
	- 1.15 - Made documentation for CameraDriverInterface::CCQueryTemperature clearer.
	- 1.16 - Added HardwareModelOverrideInterface
	- 1.17 - Minor documentation update.
	- 1.18 - Added MultiConnectionDeviceInterface, PreExposureTaskInterface for cameras.
	- 1.19 - Refresh.
	- 1.20 - Added DriverSlewsToParkPositionInterface.
	- 1.21 - Added CameraDependentSettingInterface, deprecated ExtendedCameraInterface.

*/

/*!	\page x2SharingASerialPort Sharing a Serial Port
	Sharing a serial port

	See MultiConnectionDeviceInterface.
*/

/*!
\mainpage
<CENTER><H1>The X2 Standard</H1>

TheSkyX's Cross-Platform, Plug In, Device Driver Architecture</CENTER>

<B>X2 Features</B>


- Cross-platform (Windows/Mac/Linux)
- Based upon C++ standard.  Minimum dependencies for easy portability/maintainability across operating systems.  
- Smallest possible driver footprint. Only code specific to the hardware is in the driver, helpful cross platform interfaces are supplied (see \ref Tool).
- Qt is NOT required.  Allows third parties to develop drivers independent of any cross-platform library.   
- Suitable architecture for hardware manufacturers to rely upon for their native, device driver development.  
- Consumable from most every programming language (thin operating system specific callable layering required).
- Architected upon the basic principles of object oriented programming namely encapsulation, polymorphism, and inheritance.  
	- Inheritance is used carefully where an interface (a C++ class with one or more pure virtual functions) purposefully hides implementation from caller (TheSkyX) minimizing dependencies while focusing the interface on one task.
	- Keeps client (TheSkyX) code more managable.
- Modular in terms of levels of support. 
	- Can handle devices of a given kind with a broad range of capabilities without being plagued with a "CanXXX" for every property/method.
	- Basic or "essence" support isn't plagued/complicated by "no op" stubs that must be re-implemented for devices that don't have such a capability.
	- Flexible for adding a new capability not found in any other device in kind.  Only the device with the new feature needs recompiled not all devices in kind. 
		- All other devices don't have to be brought up to the same level of support.
		- Clients (TheSkyX) wanting to leverage new capability must of course be updated (recompiled) to take advantage of new capability.
- Easy to implement features in devices not up to superset.  Clients (TheSkyX) compatible with superset automatically leverage new capability.
- Shows/provides a way (means) to evolve.
- Not a native "discovery" methodology (but discovery standard could be accommodated).
- Supports control of an open-ended number of devices (coming to TheSkyX) along with their persistence .

<B>Introduction</B>

One of the main goals of the X2 standard is to make it possible and easy for third parties to write and maintain their own hardware drivers compatible with TheSkyX 
on all operating systems it supports.  In addition, the X2 standard is by nature extensible, that is, it can grow at the optional, interface level without 
all drivers or clients needing to be simultaneously brought up to the same level or even recompiled for that matter.  
 
\ref x2howto

\ref x2driverinstall

\ref x2changelog
*/

/*!
\brief The AsymmetricalEquatorialInterface for equtorial mounts.

\ingroup Interface

If a X2 mount driver implements this interface, the mount is an asymmetrical equtorial mount (e.g. GEM or cross-axis).
\sa SymmetricalEquatorialInterface
*/

class AsymmetricalEquatorialInterface 
{
public:

	virtual ~AsymmetricalEquatorialInterface(){}

	/*!
	The default implementation returns the appropriate type of mount.
	*/
	MountTypeInterface::Type mountType(){return MountTypeInterface::Asymmetrical_Equatorial;}

	/*!
	If knowsBeyondThePole() returns false, the mount
	cannot distinguish unambiguosly if the OTA end of the declination axis 
	is either east or west of the pier. This somewhat restricts use of the 
	mount with TPoint - the mount must always have the OTA end of the declination 
	axis higher than the counterweights. In other words, the mount should not slew past the meridian.
	*/
	virtual bool knowsBeyondThePole() {return false;}

	/*!
	If knowsBeyondThePole() returns true,
	then beyondThePole() tells TheSkyX unambiguously 
	if the OTA end of the declination axis 
	is either east (0) or west of the pier (1).
	Note, the return value must be correct even
	for cases where the OTA end of the Dec axis 
	is lower than the counterweights.
	*/
	virtual int beyondThePole(bool& bYes){bYes=false; return 0;}
	
	/*!
	Return the hour angle at which the mount automatically flips.
	*/
	virtual double flipHourAngle() {return 0;}

	/*!
	Return the east and west hour angle limits.
	*/
	virtual int gemLimits(double& dHoursEast, double& dHoursWest){dHoursEast=dHoursWest=0;return 0;}

};

#endif