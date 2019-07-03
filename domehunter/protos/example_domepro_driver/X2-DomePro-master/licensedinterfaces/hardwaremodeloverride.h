#ifndef _HardwareModelOverrideInterface_H
#define _HardwareModelOverrideInterface_H

#define HardwareModelOverrideInterface_Name "com.bisque.TheSkyX.HardwareModelOverrideInterface/1.0"

/*!   
\brief The HardwareModelOverrideInterface allows x2 drivers to provide a textual model name other than the
'Model' field found in the corresponding company specific 'hardwarelist.txt' file.

\ingroup Interface

This interface is optional.  It is not recommended to support this interface unless it is absolutely necessary.  
Software Bisque has found that customers expect to be able to explicitly choose their hardware model and if they 
cannot, they will usually require technical support.
The recommended way x2 drivers list their hardware model(s) is to explicitly list each model in their company 
specific "hardwarelist.txt" (see the "hardwarelist.txt" for details).  The "hardwareList.txt" convention provides 
a simple way to list n models that point to one or more drivers without requiring any hardware i/o calls.

The HardwareModelOverrideInterface allows x2 drivers to provide a textual model name other than what is listed
in the company specific hardware list.  Examples of implementing this interface may include cases where listing all 
possible models isn't desirable or if the x2 driver is consuming another entire driver model where the 
actual model of hardware is purposefully hidden and if and only if the real model is known after connection.

TheSkyX build 6655 or later is required for this optional interface to work.  Earlier builds simply ignore it.

See TheSkyXFacadeForDriversInterface::build() to determine the build of TheSky in use an act accordingly based on your requirements. 

*/

class HardwareModelOverrideInterface
{
public:

	virtual ~HardwareModelOverrideInterface(){}

public:
	//HardwareModelOverrideInterface
	/*!Return a model name.*/
	virtual void hardwareModelOverride(BasicStringInterface& str)=0;

};

#endif