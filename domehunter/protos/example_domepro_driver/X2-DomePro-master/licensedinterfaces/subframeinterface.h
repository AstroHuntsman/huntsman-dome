#ifndef _SubframeInterface_H
#define _SubframeInterface_H

#define SubframeInterface_Name "com.bisque.TheSkyX.SubframeInterface/1.0"

/*!   
\brief The SubframeInterface allows camera drivers to enable subframe support.

\ingroup Interface

This interface is optional.  TheSkyX queries camera drivers for implementation of this interface
and if supported the user interface in TheSkyX for taking subframe images from cameras is enabled.
Don't forget to respond accordingly in your queryAbstraction().

Warning, this interface represents a new, different and mutually exlusive implementation of 
CameraDriverInterface::CCSetBinnedSubFrame().  The initial release of TheSkyX didn't allow subframes, however, the 
CameraDriverInterface did have the CCSetBinnedSubFrame() and it was called.

As of build 6200, TheSkyX supports camera subframes (along with autoguiding).  To avoid the possibility of breaking existing x2 camera drivers that 
may have utilized the information TheSkyX sent in the original call to CameraDriverInterface::CCSetBinnedSubFrame() and or 
were never tested with different subframe sizes, implementation of this SubframeInterface is required to enable subframes.  
This way published drivers cannot be "broken" and those drivers will have to be "upgraded" to allow subframe support in TheSkyX.

Please note, CCSetBinnedSubFrame3 call below is different because the last two parameters are 
width and height instead of bottom and right as in the original CCSetBinnedSubFrame().  

If published drivers actually use the information sent by TheSkyX's original call to 
CameraDriverInterface::CCSetBinnedSubFrame(), in order to maintain backward compatibility with older 
versions of TheSkyX, drivers will still need to work with the old call CCSetBinnedSubFrame() 
plus going forward, implement this SubframeInterface.

*/

class SubframeInterface
{
public:

	virtual ~SubframeInterface(){}

public:
	//SubframeInterface
	/*!TheSkyX calls this fuunction to give the driver the size of the subframe in binned pixels. If there is no subframe, the size represents the entire CCD.
	  For example, a CCD chip that has a width of 1500 pixels and a height of 1200 will have 0,0,1500,1200 for left, top, nWidth, nHeight.*/
	virtual int CCSetBinnedSubFrame3(const enumCameraIndex& Camera, const enumWhichCCD& CCDOrig, const int& nLeft, const int& nTop, const int& nWidth, const int& nHeight)=0;

};

#endif