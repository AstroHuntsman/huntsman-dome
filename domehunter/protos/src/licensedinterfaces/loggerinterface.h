#ifndef _LoggerInterface_H_
#define _LoggerInterface_H_

#define LoggerInterface_Name "com.bisque.TheSkyX.Components.LoggerInterface/1.0"

/*!   
\brief The LoggerInterface is a cross-platform logging utility passed to X2 implementors to show real-time,
driver logging information in TheSkyX.  

\ingroup Tool

This interface is probably most useful while developing and debugging an x2 driver.  To a lesser 
extent it can also be used to help customers troubleshoot driver related issues, but only when 
absolutely necessary. In other words, x2 drivers should work out-of-the-box and customers 
should not to have enabling logging and or wade through logs to help find and fix issues, 
although in rare circumstances, this might be necessary.

To enable logging, an x2 driver must respond appropriately to queryAbstraction() 
when queried for logger interface. Please see the x2dome example for sample code on how
to respond to queryAbstraction:

\dontinclude x2dome.cpp
\skip int X2Dome::queryAbstraction
\until {
...
\skip optional LoggerInterface
\until GetLogger
...
\skip }
\line }

where GetLogger() returns a pointer to the LoggerInterface passed in the constructor;

and how to send output to the TheSkyX's logging window:

\dontinclude x2dome.cpp
\skip int X2Dome::dapiGetAzEl
\until GetLogger()->out

An x2 implementor might choose to only support the logger interface in debug or special builds and
not for release builds. In any case, it is acceptable to leave in your code all the logger 
output calls as they are very efficient and don't actively do something unless 1) queryAbstraction 
enables logging and 2) the customer has displayed the corresponding logging window in TheSkyX.

TheSkyX's user interface will not give an option to show a logging window unless the underlining x2 driver
responds to queryAbstraction() appropriately above.

This interface is optional.

Dome logging requires TheSkyX build 4767 and later (mount logging has been present since TheSkyX's inception).

See TheSkyXFacadeForDriversInterface::build() to determine the build of TheSky in use an act accordingly based on your requirements. 

Tested and works on Windows, Mac, Ubuntu Linux.
*/

class LoggerInterface
{
public:
	virtual ~LoggerInterface(){};
	
public:
	/*! Have a string logged in TheSkyX's Communication Log window.*/
	virtual int out(const char* szLogThis)=0;

	/*! Return the number of packets, retries and failures associated with device io if appropriate.*/
	virtual void packetsRetriesFailuresChanged(const int& p, const int& r, const int& f)=0;

};

#endif
//Linux wants a 'newline' at the end of every source file - don't delete the one after this line
