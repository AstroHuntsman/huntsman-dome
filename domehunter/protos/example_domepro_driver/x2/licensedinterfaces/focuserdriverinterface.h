#ifndef _FocuserDriverInterface_H
#define _FocuserDriverInterface_H

#ifdef THESKYX_FOLDER_TREE
#include "imagingsystem/hardware/interfaces/licensed/driverrootinterface.h"
#include "imagingsystem/hardware/interfaces/licensed/deviceinfointerface.h"
#include "imagingsystem/hardware/interfaces/licensed/driverinfointerface.h"
#include "imagingsystem/hardware/interfaces/licensed/linkinterface.h"
#include "imagingsystem/hardware/interfaces/licensed/focuser/focusergotointerface2.h"
#include "sberror.h"
#else
#include "../../licensedinterfaces/driverrootinterface.h"
#include "../../licensedinterfaces/deviceinfointerface.h"
#include "../../licensedinterfaces/driverinfointerface.h"
#include "../../licensedinterfaces/linkinterface.h"
#include "../../licensedinterfaces/focuser/focusergotointerface2.h"
#endif

/*!
\brief The FocuserDriverInterface allows an X2 implementor to a write X2 focuser driver.

\ingroup Driver

See the X2Focuser for an example.
*/
class FocuserDriverInterface : public DriverRootInterface, public LinkInterface, public HardwareInfoInterface, public DriverInfoInterface, public FocuserGotoInterface2
{
public:
	virtual ~FocuserDriverInterface(){}

	/*!\name DriverRootInterface Implementation
	See DriverRootInterface.*/
	//@{ 
	virtual DeviceType							deviceType(void)							  {return DriverRootInterface::DT_FOCUSER;}
	virtual int									queryAbstraction(const char* pszName, void** ppVal) = 0;
	//@} 

	/*!\name DriverInfoInterface Implementation
	See DriverInfoInterface.*/
	//@{ 
	virtual void								driverInfoDetailedInfo(BasicStringInterface& str) const		{};
	virtual double								driverInfoVersion(void) const								{return 0.0;}
	//@} 

	/*!\name HardwareInfoInterface Implementation
	See HardwareInfoInterface.*/
	//@{ 
	virtual void deviceInfoNameShort(BasicStringInterface& str) const				{};
	virtual void deviceInfoNameLong(BasicStringInterface& str) const				{};	
	virtual void deviceInfoDetailedDescription(BasicStringInterface& str) const		{};
	virtual void deviceInfoFirmwareVersion(BasicStringInterface& str)				{};
	virtual void deviceInfoModel(BasicStringInterface& str)							{};
	//@} 

	/*!\name LinkInterface Implementation
	See LinkInterface.*/
	//@{ 
	virtual int									establishLink(void)						= 0;
	virtual int									terminateLink(void)						= 0;
	virtual bool								isLinked(void) const					= 0;
	//@} 

	/*!\name FocuserGotoInterface2 Implementation
	See FocuserGotoInterface2.*/
	virtual int									focPosition(int& nPosition) 			=0;
	virtual int									focMinimumLimit(int& nMinLimit) 		=0;
	virtual int									focMaximumLimit(int& nMaxLimit)			=0; 
	virtual int									focAbort()								=0;

	virtual int								startFocGoto(const int& nRelativeOffset)	= 0;
	virtual int								isCompleteFocGoto(bool& bComplete) const	= 0;
	virtual int								endFocGoto(void)							= 0;

	virtual int								amountCountFocGoto(void) const					= 0;
	virtual int								amountNameFromIndexFocGoto(const int& nZeroBasedIndex, BasicStringInterface& strDisplayName, int& nAmount)=0;
	virtual int								amountIndexFocGoto(void)=0;
	//@}


};

#endif