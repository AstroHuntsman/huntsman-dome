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
  int rc(1);
  double a(10);
  double e(20);

  AzEl request;
  request.set_return_code(rc);
  request.set_az(a);
  request.set_el(e);
  ReturnCode reply;
  ClientContext context;

	std::cout << "HX2Dome sending: " << rc << std::endl;
	if (m_pLogger)
	{
		std::string logmessage;
		logmessage = "X2Dome::establishLink...\n Message to GRPC server: " + std::to_string(rc);
    m_pLogger->out( (logmessage).c_str() );
	}

  Status status = m_pGRPCstub->dapiGotoAzEl(&context, request, &reply);

  if (status.ok())
  {
		std::cout << "HX2Dome receiving: " << reply.return_code() << std::endl;
		if (m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::establishLink... succesful.\n Message from GRPC server: " + std::to_string(reply.return_code());
			m_pLogger->out( (logreply).c_str() );
		}

    m_bLinked = true;
		// return reply.return_code();
    return SB_OK;
  }
  else
  {
    return ERR_COMMNOLINK;
  }
}

int X2Dome::terminateLink(void)
{
	if (m_pLogger)
		m_pLogger->out("X2Dome::ttterminateLink");

	m_bLinked = false;
	return SB_OK;
}

 bool X2Dome::isLinked(void) const
{
	return m_bLinked;
}

int X2Dome::queryAbstraction(const char* pszName, void** ppVal)
{
	*ppVal = NULL;

	//Add support for the optional LoggerInterface
	if (!strcmp(pszName, LoggerInterface_Name))
		*ppVal = GetLogger();

	return SB_OK;
}

//HardwareInfoInterface
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

 void X2Dome::deviceInfoFirmwareVersion(BasicStringInterface& str)
{
 	X2MutexLocker ml(GetMutex());
 	if(m_bLinked) {
 			str = "1";
 	}
 	else
 			str = "N/A";
 }

void X2Dome::deviceInfoModel(BasicStringInterface& str)
{
	X2MutexLocker ml(GetMutex());
	if(m_bLinked) {
			str = "1";
	}
	else
			str = "N/A";
}

//DriverInfoInterface
 void	X2Dome::driverInfoDetailedInfo(BasicStringInterface& str) const
{
	str = "Send help.";
}

double	X2Dome::driverInfoVersion(void) const
{
	return DRIVER_VERSION;
}


//DomeDriverInterface
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
			logreply = "X2Dome::dapiGetAzEl... succesful.\n Message from GRPC server: Az=" + std::to_string(reply.az()) + ", El=" + std::to_string(reply.el());
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

	int rc(1);
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
		logmessage = "X2Dome::dapiGotoAzEl";
    m_pLogger->out( (logmessage).c_str() );
	}

	Status status = m_pGRPCstub->dapiGotoAzEl(&context, request, &reply);

	if(status.ok())
	{
		// std::cout << "HX2Dome receiving: " <<  << std::endl;
		if(m_pLogger)
		{
			std::string logreply;
			logreply = "X2Dome::dapiGotoAzEl... succesful.\n Message from GRPC server: return code=" + std::to_string(reply.return_code());
			m_pLogger->out( (logreply).c_str() );
		}
		// return reply.return_code();
		return SB_OK;
	}
	else
	{
		return ERR_CMDFAILED;
	}
}

int X2Dome::dapiAbort(void)
{
	return SB_OK;
}

int X2Dome::dapiOpen(void)
{
	return SB_OK;
}

int X2Dome::dapiClose(void)
{
	return SB_OK;
}

int X2Dome::dapiPark(void)
{
	return SB_OK;
}

int X2Dome::dapiUnpark(void)
{
	return SB_OK;
}

int X2Dome::dapiFindHome(void)
{
	return SB_OK;
}

int X2Dome::dapiIsGotoComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}

int X2Dome::dapiIsOpenComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}

int	X2Dome::dapiIsCloseComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}

int X2Dome::dapiIsParkComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}

int X2Dome::dapiIsUnparkComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}

int X2Dome::dapiIsFindHomeComplete(bool* pbComplete)
{
	(void)pbComplete;
	return SB_OK;
}

int X2Dome::dapiSync(double dAz, double dEl)
{
	(void)dAz;
	(void)dEl;
	return SB_OK;
}
