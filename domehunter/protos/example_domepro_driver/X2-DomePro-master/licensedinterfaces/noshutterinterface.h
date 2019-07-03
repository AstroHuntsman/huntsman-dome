#ifndef _NoShutterInterface_H
#define _NoShutterInterface_H

#define NoShutterInterface_Name "com.bisque.TheSkyX.NoShutterInterface/1.0"

/*!   
\brief The NoShutterInterface allows camera drivers to report to TheSkyX if a camera does not have a shutter, primarily for use in the acquisition of dark frames.

\ingroup Interface

This interface is optional.  By default, TheSkyX assumes a camera has a shutter and if that is true this interface isn't important.  The NoShutterInterface allows 
camera drivers to report to TheSkyX if a camera does not have a shutter. Camera drivers implementing this interface and returning 'false' for bHasShutter when queried 
for shutter will cause TheSkyX to prompt the user to manually cover their telescope for all dark frames.

The NoShutterInterface can even return true for bHasShutter allowing for unified code for single x2 drivers that support multiple camera models, with and without shutters.

Don't forget to respond accordingly in your queryAbstraction().

*/

class NoShutterInterface
{
public:

	virtual ~NoShutterInterface(){}

public:
	//NoShutterInterface
	/*!TheSkyX calls this function to query the driver reguarding the existance of its controlled camera's shutter.*/
	virtual int CCHasShutter(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, bool &bHasShutter)=0;

};

#endif