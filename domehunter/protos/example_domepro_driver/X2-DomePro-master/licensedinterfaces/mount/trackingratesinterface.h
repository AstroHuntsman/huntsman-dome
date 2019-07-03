#ifndef _TrackingRatesInterface_H
#define _TrackingRatesInterface_H

#define TrackingRatesInterface_Name "com.bisque.TheSkyX.TrackingRatesInterface/1.0"

/*!
\brief The TrackingRatesInterface allows X2 mounts to support variable tracking rates. 

\ingroup Interface

*/
class TrackingRatesInterface 
{
public:

	virtual ~TrackingRatesInterface(){}

public:

	/*!Set the tracking rates.
	
	By nature the TrackingRatesInterface is for mounts the can support variable tracking rates.  There are mounts that only have two rates, sidereal rate and off.  
	A workaround to accomodate these mounts would be to respond only to those two particular cases of setTrackingRates (to see these cases, on the Telescope Tab, 
	Tools, Turn Sidereal Tracking On and Turn Tracking Off). Otherwise return ERR_COMMANDNOTSUPPORTED for rates that the mount isn't capable of, like
	tracking a asteroid, comet, etc. */
	virtual int setTrackingRates( const bool& bTrackingOn, const bool& bIgnoreRates, const double& dRaRateArcSecPerSec, const double& dDecRateArcSecPerSec)=0;

	/*!Turn off tracking.  Provided for convenience, merely calls setTrackingRates() function.*/
	virtual int trackingOff()
	{
		return setTrackingRates( false, true, 0.0, 0.0);
	}
	/*!Turn on sidereal tracking.  Provided for convenience, merely calls setTrackingRates() function.*/
	virtual int siderealTrackingOn()
	{
		return setTrackingRates( true, true, 0.0, 0.0);
	}

	/*!Return the current tracking rates.  
	
	A special case for mounts that can set rates, but not read them...
	So the TheSkyX's user interface can know this, set bTrackingOn=false and return both rates as -1000.0.

	Another special case convention, for mounts that can read rates, if bTrackingOn=false and the rates are 15.0410681 +- 0.00001 for ra
	and  0 +- 0.00001 for dec, TheSkyX's mount status will say 'Tracking off'*/
	virtual int trackingRates( bool& bTrackingOn, double& dRaRateArcSecPerSec, double& dDecRateArcSecPerSec)=0;
};

#endif