#ifndef _PreExposureTaskInterface_H
#define _PreExposureTaskInterface_H

#define PreExposureTaskInterface_Name "com.bisque.TheSkyX.PreExposureTaskInterface/1.0"

/*!   
\brief The PreExposureTaskInterface gives cameras a way to inform TheSkyX when executing CameraDriverInterface::CCStartExposure
will take longer than dExposureDuration.

\ingroup Interface

This interface is optional.  By default, when an exposure is triggered, TheSkyX will display a countdown showing when the
exposure duration set by the user has ellapsed.  However, many cameras have additional functions (such as RBI, mirror lock, etc)
that can cause the process of taking an image to take substantially longer than the exposure itself.

Implementing this interface provides camera driver producers a way to cause TheSkyX to display additional progress bars
before the actual 'exposure' progress bar.

Note that TheSkyX will continue to rely on CCIsExposureComplete to determine when an exposure has actually finished, any times
reported by this interface will be used for display purposes only.  Implementing this interface does NOT change the actual sequence
of events that take place during an exposure, but can provide useful feedback to the user.

There are two types of preexposure task that this interface deals with independantly:
Type 1) Blocking tasks that must take place before CCStartExposure begins
Type 2) Nonblocking tasks that occur after CCStartExposure begins, but while CCIsExposureComplete is "false"

Don't forget to respond accordingly in your queryAbstraction().

*/

class PreExposureTaskInterface
{
public:

	virtual ~PreExposureTaskInterface(){}

public:
	//PreExposureTaskInterface

	/* These functions provide status text for Type (1) pre-exposure tasks that take place BEFORE CCStartExposure is called. */

	/*!TheSkyX calls this function to query the number of pre-exposure tasks that will be executed before the exposure duration countdown.*/
	virtual int CCGetBlockingPreExposureTaskCount(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, int &nCount)=0;
	
	/*!TheSkyX calls this function to query the name of the task (to be displayed above the progress bar), and the expected duration of the task. */
	virtual int CCGetBlockingPreExposureTaskInfo(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int nIndex, BasicStringInterface &sName)=0;

	/*!TheSkyX calls this function to query the name of the task (to be displayed above the progress bar), and the expected duration of the task. */
	virtual int CCExecuteBlockingPreExposureTask(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int nIndex)=0;

	/* These functions provide status text for Type (2) pre-exposure tasks that take place AFTER CCStartExposure is called */

	/*!TheSkyX calls this function to query the number of pre-exposure tasks that will be executed before the exposure duration countdown.*/
	virtual int CCGetPreExposureTaskCount(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, int &nCount)=0;
	
	/*!TheSkyX calls this function to query the name of the task (to be displayed above the progress bar), and the expected duration of the task. */
	virtual int CCGetPreExposureTaskInfo(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int nIndex, double &dDuration, BasicStringInterface &sName)=0;

	/*For cameras that also implement ExtendedCameraInterface, this function will be called to let the camera know which additional argument index will be used
	  Cameras without this interface may leave the provided default implementation as-is*/
	virtual int CCSetAdditionalArgInterface(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int &nIndex) { return 0 /*SB_OK*/; }
};

#endif
