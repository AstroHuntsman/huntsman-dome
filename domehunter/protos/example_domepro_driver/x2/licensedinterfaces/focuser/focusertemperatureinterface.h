#ifndef _FocuserTemperatureInterface_H
#define _FocuserTemperatureInterface_H

#define FocuserTemperatureInterface_Name "com.bisque.TheSkyX.FocuserTemperatureInterface/1.0"

/*!   
\brief The FocuserTemperatureInterface allows focusers to report their current temperature.

\ingroup Interface

This interface is optional.  TheSkyX queries camera drivers for implementation of this interface
and if supported the user interface in TheSkyX for displaying focuser temperature is enabled.
Don't forget to respond accordingly in your queryAbstraction().

*/

class FocuserTemperatureInterface
{
public:

	virtual ~FocuserTemperatureInterface(){}

public:
	//FocuserTemperatureInterface
	/*!TheSkyX calls this fuunction to return the focuser's current temperature.
	   The value should be reported in degrees celsius.  For drivers that support multiple focusers
       where individual devices may or may not support temperature readout, returning ERR_NOT_IMPL or
       setting the temperature value to -100.0 will indicate to TSX that a temperature is unavaliable */
	virtual int focTemperature(double &dTemperature)=0;
};

#endif