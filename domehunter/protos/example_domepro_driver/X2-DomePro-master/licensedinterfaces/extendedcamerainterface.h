#ifndef _ExtendedCameraInterface_H
#define _ExtendedCameraInterface_H

#define ExtendedCameraInterface_Name "com.bisque.TheSkyX.ExtendedCameraInterface/1.0"

/*!   
\brief 

This interface is deprecated.  New development should instead use CameraDependentSettingInterface.  
This interface was deprecated in TheSky build 11525.

Existing drivers that support ExtendedCameraInterface will continure to work, but 
developers are encouraged to migrate their code to use CameraDependentSettingInterface. The change
is minimal in that the intefaces are identical except there is one additional method, namely CCGetExtendedSettingName
to supply a name for the extended setting.
A driver may support both ExtendedCameraInterface and CameraDependentSettingInterface and the latter will
prevail if the build is equal to or greater than the build when ExtendedCameraInterface was deprecated.


The ExtendedCameraInterface allows camera drivers to supply one additional argument to the standard
       CameraDriverInterface::CCStartExposure function.

\ingroup Interface

This interface is optional.  By default, TheSkyX will use the standard CCStartExposure defined in CameraDriverInterface.
However, many cameras support options which may be device-specific, or are otherwise unsupported by this default implementation
(such as RBI flush, or multiple data readout modes).

This interface adds a single additional argument to the standard CCStartExposure function, and allows the camera driver to
enumerate the potential values for this argument.  TheSkyX will then allow the user to select between these values when
commanding an exposure.

As an example, a simple implementation of this interface to support enabling/disabling RBI might:
* CCGetExtendedValueCount would return 2
* CCGetExtendedValueName would return "No RBI" as nIndex == 0, and "Using RBI" as nIndex == 1.
* CCStartExposureAdditionalArgInterface would disable RBI if passed nIndex == 0, but would enable RBI if nIndex == 1.

If an older version of TheSkyX attaches to a driver implementing this function, the standard CCStartExposure function
should be called.  By convention, this should be the equivalent of calling CCStartExposureAdditionalArgInterface with
nIndex == 0.

Don't forget to respond accordingly in your queryAbstraction().

*/

class ExtendedCameraInterface
{
public:

	virtual ~ExtendedCameraInterface(){}

public:
	//ExtendedCameraInterface
	/*!TheSkyX calls this function to query the number of possible values the extended CCStartExposure argument may take.*/
	virtual int CCGetExtendedValueCount(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, int &nCount)=0;
	
	/*!TheSkyX calls this function to query the human-readable name of each of the possible values the extended argument may take.
	   The strings returned by this function will be presented to the user for selection. */
	virtual int CCGetExtendedValueName(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int nIndex, BasicStringInterface &sName)=0;
	
	/*!	An alternative to  the standard implementation of CCStartExposure to present one additional option (nIndex), whose value must be between 0
	    and the result of CCGetExtendedValueCount - 1 */
	virtual int CCStartExposureAdditionalArgInterface(const enumCameraIndex& Cam, const enumWhichCCD CCD, const double& dTime, enumPictureType Type,
	                            const int& nABGState, const bool& bLeaveShutterAlone, const int &nIndex)=0;
};

#endif