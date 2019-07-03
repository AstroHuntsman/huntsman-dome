#ifndef _CameraDependentSettingInterface_H
#define _CameraDependentSettingInterface_H

#define CameraDependentSettingInterface_Name "com.bisque.TheSkyX.CameraDependentSettingInterface/1.0"

/*!   
\brief The CameraDependentSettingInterface allows camera drivers to supply one open-ended, additional argument to the standard
       CameraDriverInterface::CCStartExposure function.  This offers camera drivers great flexibility in what the setting
	   does along with the available options.

\ingroup Interface

This interface is optional.  By default, TheSkyX will use the standard CCStartExposure defined in CameraDriverInterface.
However, many cameras support options which may be device-specific, or are otherwise unsupported by the default implementation
of acquiring an exposure. Examples might include RBI flush, or multiple data readout modes, specialized processing, etc.

This interface adds a single additional argument to the standard CCStartExposure function, and allows the camera driver to
dictate all available values or options for this argument.  TheSkyX will then allow the user to select between these options when
commanding an exposure with the user interface or through scripting.

As an example, a company named "XYZ" might use this interface to support enabling/disabling RBI:
- CCGetExtendedSettingName would return "XYZ RBI mode"
- CCGetExtendedValueCount would return 2
- CCGetExtendedValueName would return "No RBI" as nIndex == 0, and "Using RBI" as nIndex == 1.
- CCStartExposureAdditionalArgInterface would disable RBI if passed nIndex == 0, but would enable RBI if nIndex == 1.

If an older version of TheSkyX attaches to a driver implementing this interface, the standard CCStartExposure function
will be called.  By convention, this should be the equivalent of calling CCStartExposureAdditionalArgInterface with
nIndex == 0.

When an exposure is acquired when this interface is supported, the current setting (i.e. whatever option is currently selected)
is written to the FITS header under the FITS key "CDS" with the FITS comment "Camera dependent setting".

This interface was added in TheSky build 11525.

Don't forget to respond accordingly in your queryAbstraction().

*/

class CameraDependentSettingInterface
{
public:

	virtual ~CameraDependentSettingInterface(){}

public:
	//CameraDependentSettingInterface

	/*!TheSkyX calls this function to query the human-readable name of the camera dependent setting.  The string sSettingName is displayed to user as
	the label next to the camera dependent setting. The setting name should be relatively short and meaningful. Avoid using an overly generic name.  It is strongly 
	recommended that the setting name be prepended with the company initials (or company name if short), see the detailed description for a specific example.  
	This way scripted access has a chance to uniquely identifiy the particular camera dependent setting for use in differing contexts. This setting name should 
	not arbitrarily change once published since it will act as a unique identifier for scripted use of this setting. Available options should not change either, unless added to.*/
	virtual int CCGetExtendedSettingName(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, BasicStringInterface &sSettingName)=0;

	/*!TheSkyX calls this function to query the number of possible values the extended CCStartExposure argument may take.*/
	virtual int CCGetExtendedValueCount(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, int &nCount)=0;
	
	/*!TheSkyX calls this function to query the human-readable name of each of the possible values or options the camera dependent argument may take.
	   The strings returned by this function will be presented to the user for selection. */
	virtual int CCGetExtendedValueName(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int nIndex, BasicStringInterface &sName)=0;
	
	/*!	An alternative to the standard implementation of CCStartExposure to present one additional option (nIndex), whose value must be between 0
	    and the result of CCGetExtendedValueCount - 1 */
	virtual int CCStartExposureAdditionalArgInterface(const enumCameraIndex& Cam, const enumWhichCCD CCD, const double& dTime, enumPictureType Type,
	                            const int& nABGState, const bool& bLeaveShutterAlone, const int &nIndex)=0;
};

#endif