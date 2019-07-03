#ifndef _PixelSizeInterface_H
#define _PixelSizeInterface_H

#define PixelSizeInterface_Name "com.bisque.TheSkyX.PixelSizeInterface/1.0"

/*!   
\brief The PixelSizeInterface allows camera drivers to provide the physical pixel size in microns.

\ingroup Interface

This interface is optional.  TheSkyX queries cameras for implementation of this interface
and if supported will populate the FITS header with the returned pixel size.  Don't forget to
respond accrodingly in queryAbstraction().  TheSkyX will only query for this inteferface
after successfully connecting to the camera with CCEstablishLInk().

Drivers should always return the size of the pixel in 1x1 binning and in microns.  When
populating the FITS header, TheSkyX will adjust the size according to the bin mode
in effect.
*/

class PixelSizeInterface
{
public:

	virtual ~PixelSizeInterface(){}

public:
	//PixelSizeInterface
	/*!Return the physical pixel size in 1x1 binning and in microns.*/
	virtual int PixelSize1x1InMicrons(const enumCameraIndex& Camera, const enumWhichCCD& CCD, double& x, double& y)=0;

};

#endif