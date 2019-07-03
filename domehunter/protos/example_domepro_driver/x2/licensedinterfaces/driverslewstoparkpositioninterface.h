#ifndef _DriverSlewsToParkPositionInterface_H
#define _DriverSlewsToParkPositionInterface_H

#define DriverSlewsToParkPositionInterface_Name "com.bisque.TheSkyX.DriverSlewsToParkPositionInterface/1.0"

/*!   
\brief The DriverSlewsToParkPositionInterface prevents TheSky from slewing the mount to the park position when a Park command is issued so that the mount driver can take on this responsibility.

\ingroup Interface

This interface is optional.  At this time TheSkyX only queries mounts for implementation of this interface.

Merely implementing this interface means the mount driver slews to the park position and parks the mount as well as maintains the park position.  No additional implementation needed.

This overrides the default behavior where upon Park, TheSky is responsible for slewing a mount to the park position, parking and maintaining that position.

This interface was added in TheSky build 11173, see TheSkyXFacadeForDriversInterface::build.

\sa ParkInterface
*/
class DriverSlewsToParkPositionInterface
{
public:

	virtual ~DriverSlewsToParkPositionInterface(void){}
	
};

#endif