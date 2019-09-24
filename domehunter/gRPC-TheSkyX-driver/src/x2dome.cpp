#include <stdio.h>
#include <string.h>
#include "x2dome.h"

#include "licensedinterfaces/sberrorx.h"
#include "licensedinterfaces/basicstringinterface.h"
#include "licensedinterfaces/basiciniutilinterface.h"
#include "licensedinterfaces/theskyxfacadefordriversinterface.h"
#include "licensedinterfaces/sleeperinterface.h"
#include "licensedinterfaces/loggerinterface.h"
#include "licensedinterfaces/basiciniutilinterface.h"
#include "licensedinterfaces/mutexinterface.h"

// may not actually need these
#include "licensedinterfaces/serxinterface.h"
#include "licensedinterfaces/tickcountinterface.h"

X2Dome::X2Dome( const char*                          pszSelection,
								const int&                           nISIndex,
								SerXInterface*						           pSerX,
								TheSkyXFacadeForDriversInterface*    pTheSkyXForMounts,
								SleeperInterface*				             pSleeper,
								BasicIniUtilInterface*			         pIniUtil,
								LoggerInterface*				             pLogger,
								MutexInterface*					             pIOMutex,
								TickCountInterface*				           pTickCount,
								std::shared_ptr<Channel>             channel
							) : m_pGRPCstub(HX2Dome::NewStub(channel))
{
	(void)pszSelection;
	m_nPrivateISIndex			= nISIndex;
	m_pSerX							  = pSerX;
	m_pTheSkyXForMounts		= pTheSkyXForMounts;
	m_pSleeper						= pSleeper;
	m_pIniUtil						= pIniUtil;
	m_pLogger						  = pLogger;
	m_pIOMutex						= pIOMutex;
	m_pTickCount					= pTickCount;

	m_bLinked = false;
}


X2Dome::~X2Dome()
{
	if (m_pSerX)
		delete m_pSerX;
	if (m_pTheSkyXForMounts)
		delete m_pTheSkyXForMounts;
	if (m_pSleeper)
		delete m_pSleeper;
	if (m_pIniUtil)
		delete m_pIniUtil;
	if (m_pLogger)
		delete m_pLogger;
	if (m_pIOMutex)
		delete m_pIOMutex;
	if (m_pTickCount)
		delete m_pTickCount;
	// if(m_pGRPCstub)
	// 	m_pGRPCstub=NULL;
}


// The link is initialised same time as the X2Dome object is in main...
// at the moment this function is more of a "confirmLink" but TheSkyX needs this to work(?)
int X2Dome::establishLink(void)
{
	Empty request;
  AzEl reply;
  ClientContext context;

	//std::cout << "HX2Dome sending a dapiGetAzEl request to confirm link." << std::endl;
	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::establishLink -> X2Dome::dapiGetAzEl";
    m_pLogger->out( (logmessage).c_str() );
	}

	Status status = m_pGRPCstub->dapiGetAzEl(&context, request, &reply);

	if(status.ok())
	{
		m_bLinked = true;

		std::cout << "HX2Dome dapiGetAzEl return code is: " << reply.return_code() << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::establishLink [SUCCESSFUL] - "
			           "Message from GRPC server: "
								 "Az: " + std::to_string(reply.az()) +
								 ", El: " + std::to_string(reply.el()) +
								 ", return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		return SB_OK;
	}
	else
	{
		m_bLinked = false;
		return ERR_COMMNOLINK;
	}
}


// unsure what this should be used for
int X2Dome::terminateLink(void)
{
	if (m_pLogger)
		m_pLogger->out("X2Dome::terminateLink");

	m_bLinked = false;
	return SB_OK;
}


bool X2Dome::isLinked(void) const
{
	return m_bLinked;
}


// can't remember what this is supposed to do
int X2Dome::queryAbstraction(const char* pszName, void** ppVal)
{
	*ppVal = NULL;

	//Add support for the optional LoggerInterface
	if (!strcmp(pszName, LoggerInterface_Name))
		*ppVal = GetLogger();

	return SB_OK;
}


////////////////////////////////////////////////////////////////////////////////
///                        HardwareInfoInterface                             ///
////////////////////////////////////////////////////////////////////////////////

void X2Dome::deviceInfoNameShort(BasicStringInterface& str) const
{
	str = "HuntsmanDome";
}


void X2Dome::deviceInfoNameLong(BasicStringInterface& str) const
{
	str = "Huntsman Telescope Dome Controller";
}


void X2Dome::deviceInfoDetailedDescription(BasicStringInterface& str) const
{
	str = "Huntsman Telescope Dome Controller";
}


// I suppose this should query the rpi for a "firmware version" at some point
void X2Dome::deviceInfoFirmwareVersion(BasicStringInterface& str)
{
 	X2MutexLocker ml(GetMutex());
 	if(m_bLinked) {
 			str = "1";
 	}
 	else
 			str = "N/A";
 }


// I suppose this should query the rpi for a "device into model" at some point
void X2Dome::deviceInfoModel(BasicStringInterface& str)
{
	X2MutexLocker ml(GetMutex());
	if(m_bLinked) {
			str = "1";
	}
	else
			str = "N/A";
}


////////////////////////////////////////////////////////////////////////////////
///                        DriverInfoInterface                               ///
////////////////////////////////////////////////////////////////////////////////

void X2Dome::driverInfoDetailedInfo(BasicStringInterface& str) const
{
	str = "nunya.";
}

double X2Dome::driverInfoVersion(void) const
{
	return DRIVER_VERSION;
}

////////////////////////////////////////////////////////////////////////////////
///                        DomeDriverInterface                              ///
////////////////////////////////////////////////////////////////////////////////
int X2Dome::dapiGetAzEl(double* pdAz, double* pdEl)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	Empty request;
  AzEl reply;
  ClientContext context;

	// std::cout << "HX2Dome sending: " <<  << std::endl;
	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiGetAzEl";
    m_pLogger->out( (logmessage).c_str() );
	}

	Status status = m_pGRPCstub->dapiGetAzEl(&context, request, &reply);

	if(status.ok())
	{
		*pdAz = reply.az();
		*pdEl = reply.el();

		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiGetAzEl [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "Az: " + std::to_string(reply.az()) +
								 ", El: " + std::to_string(reply.el()) +
								 ", return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		return SB_OK;
	}
	else
	{
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiGotoAzEl(double dAz, double dEl)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	int rc(0);
	AzEl request;
	request.set_return_code(rc);
	request.set_az(dAz);
	request.set_el(dEl);
  ReturnCode reply;
  ClientContext context;

	// std::cout << "HX2Dome sending: " <<  << std::endl;
	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiGotoAzEl requesting "
							   "Az: " + std::to_string(request.az()) +
							   ", El: " + std::to_string(request.el()) + ".";
    m_pLogger->out( (logmessage).c_str() );
	}

	Status status = m_pGRPCstub->dapiGotoAzEl(&context, request, &reply);

	if(status.ok())
	{
		// NB with how things are, theskyx is only being told when a "gotoAzEl" is
		// completed by the rpi, so need to make sure the rpi ends up at the
		// requested position, or change this rpc to receive an AzEl message.
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiGotoAzEl [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiAbort(void)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiAbort";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	ReturnCode reply;
	ClientContext context;

	Status status = m_pGRPCstub->dapiAbort(&context, request, &reply);

	if(status.ok())
	{
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiAbort [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiOpen(void)
{
	// leaving this for now but could set this up later to operate shutter
	return SB_OK;
}


int X2Dome::dapiClose(void)
{
	// leaving this for now but could set this up later to operate shutter
	return SB_OK;
}


int X2Dome::dapiPark(void)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiPark";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	ReturnCode reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiPark(&context, request, &reply);

	if(status.ok())
	{
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiPark [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiUnpark(void)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiUnpark";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	ReturnCode reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiUnpark(&context, request, &reply);

	if(status.ok())
	{
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiUnpark [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiFindHome(void)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiFindHome";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	ReturnCode reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiFindHome(&context, request, &reply);

	if(status.ok())
	{
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiFindHome [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiIsGotoComplete(bool* pbComplete)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiIsGotoComplete";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	IsComplete reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiIsGotoComplete(&context, request, &reply);

	if(status.ok())
	{
		*pbComplete = reply.is_complete();

		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiIsGotoComplete [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


// not implementing shutter control at the moment
int X2Dome::dapiIsOpenComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}


// not implementing shutter control at the moment
int	X2Dome::dapiIsCloseComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}


int X2Dome::dapiIsParkComplete(bool* pbComplete)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiIsParkComplete";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	IsComplete reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiIsParkComplete(&context, request, &reply);

	if(status.ok())
	{
		*pbComplete = reply.is_complete();

		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiIsParkComplete [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiIsUnparkComplete(bool* pbComplete)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiIsUnparkComplete";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	IsComplete reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiIsUnparkComplete(&context, request, &reply);

	if(status.ok())
	{
		*pbComplete = reply.is_complete();

		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiIsUnparkComplete [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


int X2Dome::dapiIsFindHomeComplete(bool* pbComplete)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiIsFindHomeComplete";
		m_pLogger->out( (logmessage).c_str() );
	}

	Empty request;
	IsComplete reply;
 	ClientContext context;

	Status status = m_pGRPCstub->dapiIsFindHomeComplete(&context, request, &reply);

	if(status.ok())
	{
		*pbComplete = reply.is_complete();

		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiIsFindHomeComplete [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}


// Not entirely sure what this should do? calibrate and then go to dAz?
int X2Dome::dapiSync(double dAz, double dEl)
{
	X2MutexLocker ml(GetMutex());
	if(!m_bLinked)
			return ERR_NOLINK;

	int rc(0);
	AzEl request;
	request.set_return_code(rc);
	request.set_az(dAz);
	request.set_el(dEl);
  ReturnCode reply;
  ClientContext context;

	// std::cout << "HX2Dome sending: " <<  << std::endl;
	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::dapiSync requesting sync to Az: " + std::to_string(dAz) + ", El:" + std::to_string(dEl)+".";
    m_pLogger->out( (logmessage).c_str() );
	}

	Status status = m_pGRPCstub->dapiSync(&context, request, &reply);

	if(status.ok())
	{
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiSync [SUCCESSFUL] - "
								 "Message from GRPC server: "
								 "return_code: " + std::to_string(reply.return_code()) + ".";
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		// return reply.return_code();
		return ERR_CMDFAILED;
	}
}
